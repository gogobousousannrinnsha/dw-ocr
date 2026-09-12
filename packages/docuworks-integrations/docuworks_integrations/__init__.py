"""Lightweight public API; optional backends are loaded only on use."""
from importlib import import_module

__version__ = "0.6.0"
_EXPORTS = {
    **dict.fromkeys(("annotate_rectangles", "render_text_maps"), "derivatives"),
    "process_documents": "jobs",
    **dict.fromkeys(("ocr_folder", "OcrBatchResult", "BatchDocumentResult"), "batch"),
    **dict.fromkeys(("AddRectangle", "AddMarker", "AddText", "AnnotationPlan", "ExecutionReport", "OcrRegion", "PixelPoint", "PixelRect"), "models"),
    **dict.fromkeys(("OcrEngine", "JsonOcrEngine"), "ocr"),
    **dict.fromkeys(("bounding_rects", "find_contour_rects", "read_image_size"), "opencv"),
    **dict.fromkeys(("build_ocr_plan", "build_marker_plan"), "planning"),
    **dict.fromkeys(("OcrDocumentResult", "OcrPageResult", "CanonicalOcrRegion", "load_ocr_result", "save_ocr_result", "get_region", "export_jsonl"), "results"),
    "execute_plan": "executor", "PaddleOcrEngine": "paddle", "PageTransform": "transforms",
}
__all__ = list(_EXPORTS)

def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module("." + _EXPORTS[name], __name__), name)
    globals()[name] = value
    return value
