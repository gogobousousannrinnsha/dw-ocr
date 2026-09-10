from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from docuworks_ctypes import Color
from docuworks_ctypes.simple import open_xdw
from docuworks_integrations import load_ocr_result
from docuworks_integrations.recognition import ocr_xdw


MIN_RECT_MM = 3.0

COLOR_MAP = {
    "red": Color.RED,
    "blue": Color.BLUE,
    "green": Color.GREEN,
    "black": Color.BLACK,
    "yellow": Color.YELLOW,
    "purple": Color.PURPLE,
    "teal": Color.TEAL,
}


def portable_root() -> Path:
    """Return the root directory of the self-contained portable environment."""
    here = Path(__file__).resolve().parent

    # Recommended placement:
    #   <portable-root>/scripts/ocr_all_regions_to_rectangles.py
    if (here.parent / "runtime" / "python.exe").is_file():
        return here.parent

    # Also allow placing this script directly in the portable root.
    if (here / "runtime" / "python.exe").is_file():
        return here

    raise RuntimeError(
        "Portable environment root could not be found. "
        "Place this script in <portable-root>\\scripts\\ "
        "or directly in <portable-root>."
    )


def fit_interval(
    start: float,
    length: float,
    limit: float,
    *,
    padding: float,
    minimum: float = MIN_RECT_MM,
) -> tuple[float, float]:
    """Pad an interval and ensure a minimum size without leaving the page."""
    if limit < minimum:
        raise ValueError(f"Page dimension {limit:.3f} mm is below minimum rectangle size.")

    original_start = float(start)
    original_end = float(start + length)

    left = max(0.0, original_start - padding)
    right = min(limit, original_end + padding)

    if right <= left:
        raise ValueError("OCR bounding box has an invalid dimension.")

    if right - left < minimum:
        center = (original_start + original_end) / 2.0
        left = center - minimum / 2.0
        right = center + minimum / 2.0

        if left < 0.0:
            right -= left
            left = 0.0
        if right > limit:
            left -= right - limit
            right = limit

        left = max(0.0, left)
        right = min(limit, right)

    size = right - left
    if size < minimum - 1e-9:
        raise ValueError(
            f"Could not fit a {minimum:.1f} mm rectangle inside page dimension "
            f"{limit:.3f} mm."
        )

    return left, size


def rectangle_from_bbox(
    bbox_mm: dict,
    *,
    page_width_mm: float,
    page_height_mm: float,
    padding_mm: float,
) -> dict[str, float]:
    """Convert one canonical OCR bbox_mm into a valid DocuWorks rectangle."""
    x, width = fit_interval(
        float(bbox_mm["x"]),
        float(bbox_mm["width"]),
        float(page_width_mm),
        padding=padding_mm,
    )
    y, height = fit_interval(
        float(bbox_mm["y"]),
        float(bbox_mm["height"]),
        float(page_height_mm),
        padding=padding_mm,
    )
    return {"x": x, "y": y, "width": width, "height": height}


def should_include(confidence: float | None, minimum: float) -> bool:
    if minimum <= 0.0:
        return True
    return confidence is not None and confidence >= minimum


def parse_args() -> argparse.Namespace:
    root = portable_root()

    parser = argparse.ArgumentParser(
        description=(
            "OCR every page of an XDW document and add a rectangle annotation "
            "around every recognized region to a separate output XDW."
        )
    )
    parser.add_argument("input_xdw", type=Path, help="Input XDW file")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output XDW. Default: <input_stem>_ocr_rectangles.xdw beside the input.",
    )
    parser.add_argument(
        "--model-root",
        type=Path,
        default=root / "models",
        help="PP-OCRv6 model directory. Default: portable-root\\models",
    )
    parser.add_argument(
        "--dll-path",
        type=Path,
        default=None,
        help="Optional explicit xdwapi.dll path. Usually omit this.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        choices=(300, 600),
        default=300,
        help="Rendering DPI used for OCR. Default: 300",
    )
    parser.add_argument(
        "--padding-mm",
        type=float,
        default=0.5,
        help="Padding around each OCR bbox in millimetres. Default: 0.5",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        help="Minimum OCR confidence from 0.0 to 1.0. Default 0.0 = include all.",
    )
    parser.add_argument(
        "--color",
        choices=tuple(COLOR_MAP),
        default="red",
        help="Rectangle border color. Default: red",
    )
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=root / "runs",
        help="Intermediate OCR run directory. Default: portable-root\\runs",
    )
    parser.add_argument(
        "--keep-runs",
        action="store_true",
        help=(
            "Keep full per-page OCR bundles. Without this option they are removed "
            "after their bbox/text data have been collected."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not 0.0 <= args.min_confidence <= 1.0:
        raise ValueError("--min-confidence must be between 0.0 and 1.0")
    if args.padding_mm < 0.0:
        raise ValueError("--padding-mm must be >= 0")

    input_xdw = args.input_xdw.expanduser().resolve()
    if not input_xdw.is_file():
        raise FileNotFoundError(input_xdw)
    if input_xdw.suffix.lower() != ".xdw":
        raise ValueError(f"Input must be an .xdw file: {input_xdw}")

    model_root = args.model_root.expanduser().resolve()
    for model_name in ("PP-OCRv6_medium_det", "PP-OCRv6_medium_rec"):
        model_file = model_root / model_name / "inference.yml"
        if not model_file.is_file():
            raise FileNotFoundError(model_file)

    dll_path = args.dll_path.expanduser().resolve() if args.dll_path else None
    if dll_path is not None and not dll_path.is_file():
        raise FileNotFoundError(dll_path)

    if args.output is None:
        output_xdw = input_xdw.with_name(input_xdw.stem + "_ocr_rectangles.xdw")
    else:
        output_xdw = args.output.expanduser().resolve()

    if output_xdw == input_xdw:
        raise ValueError("Output XDW must be different from the input XDW.")
    if output_xdw.exists():
        raise FileExistsError(output_xdw)

    output_xdw.parent.mkdir(parents=True, exist_ok=True)

    report_path = output_xdw.with_name(output_xdw.stem + "_ocr_report.json")
    if report_path.exists():
        raise FileExistsError(report_path)

    # Determine page count without modifying the source.
    with open_xdw(input_xdw, writable=False, dll_path=dll_path) as document:
        page_count = document.core.page_count

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    runs_parent = args.runs_dir.expanduser().resolve()
    runs_parent.mkdir(parents=True, exist_ok=True)
    session_dir = runs_parent / f"{input_xdw.stem}-{timestamp}"
    session_dir.mkdir(exist_ok=False)

    print(f"Input       : {input_xdw}")
    print(f"Output      : {output_xdw}")
    print(f"Pages       : {page_count}")
    print(f"DPI         : {args.dpi}")
    print(f"Models      : {model_root}")
    print(f"Session dir : {session_dir}")
    print()

    pages_for_annotation: list[dict] = []
    total_recognized = 0

    # OCR all pages first. The output XDW is not created until OCR has succeeded.
    for page_number in range(1, page_count + 1):
        page_run = session_dir / f"page-{page_number:04d}"
        print(f"[OCR {page_number}/{page_count}] starting...")

        try:
            ocr_xdw(
                input_xdw,
                page_run,
                model_root,
                page=page_number,
                dpi=args.dpi,
                dll_path=dll_path,
            )
        except ValueError as exc:
            # Blank/no-text pages should not abort the entire document.
            if "OCR found no text" in str(exc):
                print(f"[OCR {page_number}/{page_count}] no text found; skipping.")
                pages_for_annotation.append(
                    {
                        "page": page_number,
                        "page_width_mm": None,
                        "page_height_mm": None,
                        "regions": [],
                    }
                )
                if not args.keep_runs:
                    shutil.rmtree(page_run, ignore_errors=True)
                continue
            raise

        result = load_ocr_result(page_run)
        if len(result.pages) != 1 or result.pages[0].page != page_number:
            raise RuntimeError(
                f"Unexpected OCR result page for page {page_number}: {result.pages}"
            )

        page_result = result.pages[0]
        selected_regions = []

        for region in page_result.regions:
            total_recognized += 1
            if not should_include(region.confidence, args.min_confidence):
                continue

            rect = rectangle_from_bbox(
                region.bbox_mm,
                page_width_mm=page_result.page_width_mm,
                page_height_mm=page_result.page_height_mm,
                padding_mm=args.padding_mm,
            )

            selected_regions.append(
                {
                    "id": region.id,
                    "text": region.text,
                    "confidence": region.confidence,
                    "bbox_mm": dict(region.bbox_mm),
                    "rectangle_mm": rect,
                }
            )

        pages_for_annotation.append(
            {
                "page": page_number,
                "page_width_mm": page_result.page_width_mm,
                "page_height_mm": page_result.page_height_mm,
                "regions": selected_regions,
            }
        )

        print(
            f"[OCR {page_number}/{page_count}] "
            f"recognized={len(page_result.regions)}, rectangles={len(selected_regions)}"
        )

        if not args.keep_runs:
            shutil.rmtree(page_run, ignore_errors=True)

    # OCR finished. Work only on a copy of the source.
    shutil.copy2(input_xdw, output_xdw)

    rectangles_added = 0
    try:
        with open_xdw(output_xdw, writable=True, dll_path=dll_path) as document:
            for page_data in pages_for_annotation:
                if not page_data["regions"]:
                    continue

                page = document.page(page_data["page"])

                for region in page_data["regions"]:
                    rect = region["rectangle_mm"]
                    page.rectangle(
                        x=rect["x"],
                        y=rect["y"],
                        width=rect["width"],
                        height=rect["height"],
                        border_color=COLOR_MAP[args.color],
                        border_visible=True,
                        fill_visible=False,
                    )
                    rectangles_added += 1

                print(
                    f"[RECT page {page_data['page']}] "
                    f"added={len(page_data['regions'])}"
                )

            document.save()
    except Exception:
        # Do not leave a file that may look completed if annotation/save failed.
        try:
            output_xdw.unlink(missing_ok=True)
        except OSError:
            pass
        raise

    report = {
        "source_xdw": str(input_xdw),
        "output_xdw": str(output_xdw),
        "page_count": page_count,
        "dpi": args.dpi,
        "model_root": str(model_root),
        "padding_mm": args.padding_mm,
        "min_confidence": args.min_confidence,
        "border_color": args.color,
        "recognized_regions": total_recognized,
        "rectangles_added": rectangles_added,
        "session_dir": str(session_dir),
        "full_ocr_bundles_kept": bool(args.keep_runs),
        "pages": pages_for_annotation,
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print()
    print("Completed.")
    print(f"Recognized regions : {total_recognized}")
    print(f"Rectangles added   : {rectangles_added}")
    print(f"Output XDW         : {output_xdw}")
    print(f"Report             : {report_path}")
    if args.keep_runs:
        print(f"OCR bundles        : {session_dir}")
    else:
        print(f"Session directory  : {session_dir} (per-page bundles cleaned up)")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.", file=sys.stderr)
        raise SystemExit(130)
