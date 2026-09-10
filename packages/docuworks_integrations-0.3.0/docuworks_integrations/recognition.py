"""Recognition producer. The legacy producer remains available as a Python compatibility API."""
from pathlib import Path
import importlib.metadata as md
import platform
import shutil
import time
import uuid
from .results import read_json, write_json, sha256


def ocr_xdw(input_xdw, run_dir, model_root, *, page=1, dpi=300, dll_path=None, engine=None):
    from .workflow import ocr_xdw as legacy_recognize
    from .legacy_results import convert_ocr_run
    output=Path(run_dir).resolve()
    if output.exists(): raise FileExistsError(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    staging=output.parent/('.recognition-'+uuid.uuid4().hex)
    started=time.perf_counter()
    try:
        legacy_recognize(input_xdw,staging,model_root,page=page,dpi=dpi,dll_path=dll_path,engine=engine)
        meta=read_json(staging/'page-info.json')
        packages={}
        for name in ('paddleocr','paddlex','paddlepaddle-gpu'):
            try: packages[name]=md.version(name)
            except md.PackageNotFoundError: packages[name]=None
        models={}
        for name in ('PP-OCRv6_medium_det','PP-OCRv6_medium_rec'):
            folder=Path(model_root)/name
            models[name]={p.name:sha256(p) for p in sorted(folder.glob('*')) if p.is_file()}
        provenance=dict(engine='PaddleOCR' if engine is None else type(engine).__name__,packages=packages,
            models=models,device='gpu:0' if engine is None else 'injected',python=platform.python_version(),
            dll_path=meta.get('dll_path'),elapsed_seconds=time.perf_counter()-started,
            preprocessing=dict(document_orientation=False,unwarping=False,textline_orientation=False))
        result=convert_ocr_run(staging,output,ocr_metadata=provenance,new_run_id=str(uuid.uuid4()))
        return read_json(result.root/'manifest.json')
    except Exception as exc:
        if not output.exists():
            output.mkdir()
            write_json(output/'error.json',dict(status='FAILED',type=type(exc).__name__,message=str(exc)))
            if (staging/'ocr-raw.json').exists(): shutil.copyfile(staging/'ocr-raw.json',output/'raw-paddle.json')
        raise
    finally:
        if staging.exists(): shutil.rmtree(staging)
