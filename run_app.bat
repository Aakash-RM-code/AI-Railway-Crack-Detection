@echo off
rem Launches the Railway Crack Detection dashboard with Python 3.11
rem (the interpreter this project is verified on). Plain `python`/`py`
rem on this machine resolve to Python 3.14.
setlocal
set "PY311=C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe"
pushd "D:\Python\crack_det_v_1"
if exist "%PY311%" (
    "%PY311%" app.py
) else (
    py -3.11 app.py
)
popd
endlocal
