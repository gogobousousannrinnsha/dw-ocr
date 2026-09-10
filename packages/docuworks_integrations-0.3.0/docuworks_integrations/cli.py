from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


def read_image_size(path):
    from .opencv import read_image_size as implementation
    return implementation(path)



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docuworks-integrations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    annotate = subparsers.add_parser("annotate-image")
    annotate.add_argument("--image", required=True, type=Path)
    annotate.add_argument("--regions-json", required=True, type=Path)
    annotate.add_argument("--page-width-mm", required=True, type=float)
    annotate.add_argument("--page-height-mm", required=True, type=float)
    annotate.add_argument("--page", type=int, default=1)
    annotate.add_argument("--input-xdw", required=True, type=Path)
    annotate.add_argument("--output-xdw", required=True, type=Path)
    annotate.add_argument("--confidence-threshold", type=float, default=0.0)
    annotate.add_argument("--font-size", type=float, default=12.0)
    annotate.add_argument("--dll-path", type=Path)
    annotate.add_argument("--codepage", type=int)
    annotate.add_argument("--dry-run", action="store_true")
    annotate.add_argument("--report", type=Path)
    ocr = subparsers.add_parser("ocr-xdw")
    ocr.add_argument("--input-xdw", required=True, type=Path)
    ocr.add_argument("--run-dir", required=True, type=Path)
    ocr.add_argument("--model-root", required=True, type=Path)
    ocr.add_argument("--page", type=int, default=1)
    ocr.add_argument("--dpi", type=int, choices=(300, 600), default=300)
    ocr.add_argument("--dll-path", type=Path)
    mark = subparsers.add_parser("mark-region")
    mark.add_argument("--run-dir", required=True, type=Path)
    mark.add_argument("--region-id", required=True)
    mark.add_argument("--input-xdw", type=Path)
    mark.add_argument("--output-xdw", required=True, type=Path)
    mark.add_argument("--dry-run", action="store_true")
    mark.add_argument("--dll-path", type=Path)
    convert = subparsers.add_parser("convert-ocr-run")
    convert.add_argument("--run-dir", required=True, type=Path)
    convert.add_argument("--output-dir", required=True, type=Path)
    export = subparsers.add_parser("export-ocr")
    export.add_argument("--run-dir", required=True, type=Path)
    export.add_argument("--format", required=True, choices=("jsonl",))
    export.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "convert-ocr-run":
        from .legacy_results import convert_ocr_run
        result = convert_ocr_run(args.run_dir, args.output_dir)
        print(json.dumps({"run_id": result.run_id, "output_dir": str(result.root)}))
        return 0
    if args.command == "export-ocr":
        from .results import load_ocr_result, export_jsonl
        print(export_jsonl(load_ocr_result(args.run_dir), args.output))
        return 0
    if args.command in ("ocr-xdw", "mark-region"):
        if args.command == "ocr-xdw":
            from .recognition import ocr_xdw
            payload = ocr_xdw(args.input_xdw, args.run_dir, args.model_root, page=args.page, dpi=args.dpi, dll_path=args.dll_path)
        else:
            from .consumers import mark_region
            payload = mark_region(args.run_dir, args.region_id, args.output_xdw, dry_run=args.dry_run, dll_path=args.dll_path, input_xdw=args.input_xdw)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.command != "annotate-image":
        raise AssertionError(args.command)
    if args.dry_run and args.report is not None:
        raise ValueError("--dry-run writes JSON only to stdout; --report is not allowed")
    from .executor import execute_plan
    from .ocr import JsonOcrEngine
    from .planning import build_ocr_plan
    from .transforms import PageTransform
    width, height = read_image_size(args.image)
    transform = PageTransform(width, height, args.page_width_mm, args.page_height_mm)
    plan = build_ocr_plan(
        args.image,
        JsonOcrEngine(args.regions_json),
        transform,
        page=args.page,
        confidence_threshold=args.confidence_threshold,
        font_size=args.font_size,
    )
    report = execute_plan(
        plan,
        args.input_xdw,
        args.output_xdw,
        dry_run=args.dry_run,
        dll_path=args.dll_path,
        codepage=args.codepage,
    )
    payload = {"plan": plan.to_dict(), "execution": report.to_dict()}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    print(rendered)
    if args.report is not None:
        report_path = args.report.expanduser().resolve()
        if report_path.exists():
            raise FileExistsError(report_path)
        report_path.write_text(rendered + "\n", encoding="utf-8")
    return 0
