#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements.txt
export PORT="${PORT:-9844}"
python backend.py
