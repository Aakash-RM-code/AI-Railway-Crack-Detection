# Launches the Railway Crack Detection dashboard with the verified interpreter.
# The project is verified on Python 3.11. Plain `python` / `py` on this machine
# resolves to Python 3.14 (first on PATH and the `py` default), which can leave
# the app on an unverified interpreter.
$ErrorActionPreference = "Stop"

$py311 = "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe"
$project = "D:\Python\crack_det_v_1"

Push-Location $project
try {
    if (Test-Path $py311) {
        & $py311 app.py
    } else {
        & py -3.11 app.py
    }
} finally {
    Pop-Location
}
