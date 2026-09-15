@echo off
setlocal
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONNOUSERSITE=1"
set "PYTHONUTF8=1"
set "DW_OCR_CACHE=%~dp0cache"
set "ROOT=%~dp0"
"%ROOT%runtime\python.exe" -I -X utf8 -m pip install --no-index --find-links "%ROOT%wheelhouse" --force-reinstall --no-deps docuworks-ctypes==1.0.0 docuworks-integrations==0.7.0
"%ROOT%runtime\python.exe" -I -X utf8 -m pip check
