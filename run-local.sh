#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ ! -f "venv/Scripts/activate" ]; then
  echo "Error: venv not found at venv/Scripts/activate"
  echo "Create it first: python -m venv venv"
  exit 1
fi

source venv/Scripts/activate
python -m pip install -r v1/requirements.txt

cd v1
python -m flask --app api.vision_extract run --host 127.0.0.1 --port "${PORT:-5000}"
