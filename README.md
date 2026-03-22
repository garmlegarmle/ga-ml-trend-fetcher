# GA-ML Trend Fetcher

Cross-platform desktop downloader for the GA-ML trend analyzer.

## What it does

- Opens a small desktop UI on macOS and Windows
- Lets the user enter one ticker and choose a save folder
- Downloads recent daily OHLCV data
- Writes one analysis-ready CSV for the GA-ML web uploader

## CSV schema

The generated file uses this column order:

```csv
symbol,date,open,high,low,close,adj_close,volume
```

The downloader keeps the most recent `260` trading bars by default so the web analyzer can render the latest `200` bars while still warming up longer indicators.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Build

### macOS

```bash
./scripts/build_macos.sh
```

### Windows

Run:

```bat
scripts\build_windows.bat
```

## Release automation

`.github/workflows/release.yml` builds macOS and Windows artifacts on tags and publishes zipped deliverables to GitHub Releases.

## Notes

- Unsigned binaries will show macOS Gatekeeper or Windows SmartScreen warnings.
- The downloader only writes a local CSV. It does not upload the file anywhere.
