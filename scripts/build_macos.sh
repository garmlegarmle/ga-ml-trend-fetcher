#!/bin/sh
set -eu

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --windowed --name GA-ML-TrendFetcher main.py

cd "$ROOT_DIR/dist"
rm -f GA-ML-TrendFetcher-macos.zip
zip -r GA-ML-TrendFetcher-macos.zip GA-ML-TrendFetcher.app
