from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docuworks_integrations import load_ocr_result


DEFAULT_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\YuGothR.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
    r"C:\Windows\Fonts\BIZ-UDGothicR.ttc",
    r"C:\Windows\Fonts\BIZ-UDGothicB.ttc",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
]


def portable_root() -> Path:
    """Return the root of the self-contained portable environment."""
    here = Path(__file__).resolve().parent
    if (here.parent / "runtime" / "python.exe").is_file():
        return here.parent
    if (here / "runtime" / "python.exe").is_file():
        return here
    return here.parent


def resolve_font_path(explicit: Path | None) -> Path | None:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return path

    windir = os.environ.get("WINDIR")
    candidates: list[Path] = []
    if windir:
        fonts_dir = Path(windir) / "Fonts"
        candidates.extend([
            fonts_dir / "YuGothM.ttc",
            fonts_dir / "YuGothR.ttc",
            fonts_dir / "meiryo.ttc",
            fonts_dir / "msgothic.ttc",
            fonts_dir / "BIZ-UDGothicR.ttc",
            fonts_dir / "BIZ-UDGothicB.ttc",
            fonts_dir / "arial.ttf",
            fonts_dir / "calibri.ttf",
        ])

    candidates.extend(Path(p) for p in DEFAULT_FONT_CANDIDATES)

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def safe_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.strip("\n")
    return text if text else " "


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    width: int,
    height: int,
    font_path: Path | None,
    *,
    min_size: int = 8,
    max_size: int = 96,
):
    width = max(1, int(width))
    height = max(1, int(height))

    def load(size: int):
        if font_path is None:
            return ImageFont.load_default()
        return ImageFont.truetype(str(font_path), size=size)

    if font_path is None:
        font = ImageFont.load_default()
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=1)
        return font, bbox

    for size in range(max_size, min_size - 1, -1):
        font = load(size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=1)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        if text_w <= width and text_h <= height:
            return font, bbox

    font = load(min_size)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=1)
    return font, bbox


def render_text_patch(
    text: str,
    width: int,
    height: int,
    font_path: Path | None,
    *,
    fg=(0, 0, 0, 255),
    bg=(255, 255, 255, 0),
    border=None,
    margin: int = 2,
    min_font: int = 8,
    max_font: int = 96,
) -> Image.Image:
    width = max(1, int(round(width)))
    height = max(1, int(round(height)))
    patch = Image.new("RGBA", (width, height), bg)
    draw = ImageDraw.Draw(patch)

    usable_w = max(1, width - margin * 2)
    usable_h = max(1, height - margin * 2)
    font, bbox = fit_font(draw, text, usable_w, usable_h, font_path, min_size=min_font, max_size=max_font)

    x = margin - bbox[0]
    y = margin - bbox[1]

    draw.multiline_text((x, y), text, font=font, fill=fg, spacing=1)

    if border is not None:
        draw.rectangle((0, 0, width - 1, height - 1), outline=border, width=1)

    return patch


def clamp_box(x: int, y: int, w: int, h: int, page_w: int, page_h: int) -> tuple[int, int, int, int]:
    x = max(0, min(int(round(x)), max(0, page_w - 1)))
    y = max(0, min(int(round(y)), max(0, page_h - 1)))
    w = max(1, int(round(w)))
    h = max(1, int(round(h)))
    if x + w > page_w:
        w = max(1, page_w - x)
    if y + h > page_h:
        h = max(1, page_h - y)
    return x, y, w, h


def page_output_dir(page_result) -> Path:
    return Path(page_result.image).parent


def generate_for_page(
    result_root: Path,
    page_result,
    font_path: Path | None,
    *,
    overwrite: bool = False,
    text_map_boxes: bool = True,
) -> dict:
    image_path = result_root / page_result.image
    if not image_path.is_file():
        raise FileNotFoundError(image_path)

    with Image.open(image_path) as source:
        original = source.convert("RGBA")

    page_w, page_h = original.size
    text_map = Image.new("RGBA", (page_w, page_h), (255, 255, 255, 255))
    overlay = original.copy()
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")

    placed = 0
    skipped = 0

    for region in page_result.regions:
        text = safe_text(region.text)
        bbox = region.bbox_px
        x, y, w, h = clamp_box(
            bbox["x"], bbox["y"], bbox["width"], bbox["height"], page_w, page_h
        )

        text_patch = render_text_patch(
            text,
            w,
            h,
            font_path,
            fg=(0, 0, 0, 255),
            bg=(255, 255, 255, 255),
            border=(200, 200, 200, 255) if text_map_boxes else None,
            margin=2,
        )
        text_map.alpha_composite(text_patch, (x, y))

        overlay_draw.rectangle((x, y, x + w - 1, y + h - 1), outline=(220, 32, 32, 255), width=2)
        overlay_patch = render_text_patch(
            text,
            w,
            h,
            font_path,
            fg=(0, 0, 0, 255),
            bg=(255, 255, 255, 210),
            border=(255, 180, 0, 255),
            margin=2,
        )
        overlay.alpha_composite(overlay_patch, (x, y))
        placed += 1

    out_dir = result_root / page_output_dir(page_result)
    out_dir.mkdir(parents=True, exist_ok=True)

    text_map_path = out_dir / "text-map.png"
    overlay_path = out_dir / "overlay-text.png"

    if not overwrite:
        for path in (text_map_path, overlay_path):
            if path.exists():
                raise FileExistsError(f"{path} already exists. Use --overwrite to replace it.")

    text_map.save(text_map_path)
    overlay.save(overlay_path)

    return {
        "page": page_result.page,
        "image": str(image_path),
        "text_map": str(text_map_path),
        "overlay_text": str(overlay_path),
        "regions": len(page_result.regions),
        "placed": placed,
        "skipped": skipped,
        "page_width_px": page_w,
        "page_height_px": page_h,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate text-map.png and overlay-text.png from an existing OCR result bundle "
            "without re-running OCR."
        )
    )
    parser.add_argument("run_dir", type=Path, help="Existing OCR bundle directory containing manifest.json")
    parser.add_argument(
        "--font",
        type=Path,
        default=None,
        help="Optional TTF/TTC font path. Default: auto-detect a Japanese-capable Windows font.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing text-map.png and overlay-text.png if they already exist.",
    )
    parser.add_argument(
        "--no-text-map-boxes",
        action="store_true",
        help="Do not draw light box outlines on text-map.png.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional output report path. Default: <run_dir>/text-map-report.json",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=None,
        help="Optional one-based page number to process only one page from the bundle.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    run_dir = args.run_dir.expanduser().resolve()
    if not run_dir.is_dir():
        raise FileNotFoundError(run_dir)

    result = load_ocr_result(run_dir)
    font_path = resolve_font_path(args.font)

    if args.report is None:
        report_path = run_dir / "text-map-report.json"
    else:
        report_path = args.report.expanduser().resolve()

    pages = list(result.pages)
    if args.page is not None:
        pages = [p for p in pages if p.page == args.page]
        if not pages:
            raise ValueError(f"Page {args.page} is not present in the OCR bundle.")

    print(f"Bundle      : {run_dir}")
    print(f"Pages       : {[p.page for p in pages]}")
    print(f"Font        : {font_path if font_path else 'Pillow default font'}")
    print()

    page_reports = []
    total_regions = 0
    for page_result in pages:
        info = generate_for_page(
            run_dir,
            page_result,
            font_path,
            overwrite=args.overwrite,
            text_map_boxes=not args.no_text_map_boxes,
        )
        page_reports.append(info)
        total_regions += info["regions"]
        print(
            f"[page {page_result.page}] regions={info['regions']} "
            f"text-map={info['text_map']} overlay={info['overlay_text']}"
        )

    report = {
        "bundle_root": str(run_dir),
        "font": str(font_path) if font_path else None,
        "processed_pages": [p["page"] for p in page_reports],
        "page_count": len(page_reports),
        "total_regions": total_regions,
        "outputs": page_reports,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print()
    print("Completed.")
    print(f"Report       : {report_path}")
    print(f"Total pages  : {len(page_reports)}")
    print(f"Total regions: {total_regions}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.", file=sys.stderr)
        raise SystemExit(130)
