@echo off
setlocal

cd /d %~dp0\..
py -m pip install --upgrade pip
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --windowed --name GA-ML-TrendFetcher main.py

powershell -Command "Compress-Archive -Force -Path dist\GA-ML-TrendFetcher\* -DestinationPath dist\GA-ML-TrendFetcher-windows.zip"
