$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not $env:PORT) {
    $env:PORT = "9844"
}

& ".\.venv\Scripts\python.exe" ".\backend.py"
