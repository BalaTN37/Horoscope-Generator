# 🌟 Vedic Astrology Web App

A modern, offline-capable Vedic astrology application that generates birth charts with accurate planetary positions and house calculations.

## ✨ Features

- **Accurate Calculations**: Uses Swiss Ephemeris for precise planetary positions
- **Multiple House Systems**: Equal, Whole Sign, Placidus, Koch, Porphyry
- **Offline Location Search**: 66,000+ cities database (no internet required)
- **Auto Timezone Detection**: Automatically determines timezone from coordinates
- **Vimshottari Dasha**: Complete mahadasha, antardasha, and pratyantardasha periods
- **Current Transits**: Real-time planetary positions
- **South Indian Chart**: Traditional chart visualization
- **Multiple Ayanamsas**: Lahiri and Krishnamurti supported

## 🚀 Live Demo

[**Deploy your own for FREE**](STEP_BY_STEP_DEPLOYMENT.md) - Complete deployment guide included!

Note: Run all commands from the astrology folder. If you are at the repository root (Sep_CMDLineAstro), first change into the app folder:

Windows PowerShell (from repo root):
```powershell
cd .\astrology
```

## Features
- Input birth datetime, latitude, longitude, timezone offset
- Computes accurate sidereal longitudes (Swiss Ephemeris), ascendant, and house cusps (Equal, Whole Sign, Placidus, Koch, Porphyry)
- Simple Vimshottari mahadasha sequence (top-level, approximate start)
- Current transits (now)
- Renders a simple chart and JSON output

## Setup
1. Create and activate a Python 3.10+ environment
2. Install dependencies
3. Run the app

### Quick start (Windows PowerShell)
```powershell
cd .\astrology   # if you are at the repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in your browser. The UI offers auto timezone detection and a proper South Indian chart with clear planet placement.

### Alternative: Flask dev server
```powershell
cd .\astrology
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_APP = 'app.py'
flask run --host 0.0.0.0 --port 5000
```

## Troubleshooting
- Error: "can't open file 'C:\\...\\Sep_CMDLineAstro\\app.py'"
	- You are likely running from the repo root. Change directory into the app folder and try again:
		```powershell
		cd .\astrology
		python app.py
		```
- Dependencies not found in VS Code (import warnings): Select the .venv interpreter for this workspace (Ctrl+Shift+P → Python: Select Interpreter → choose .venv).
- Place search or timezone auto-detect slow/unavailable: Check your internet connection; these features call external services.

## Improving Accuracy
- Replace simplified Vimshottari with a full nakshatra-based implementation (remaining balance, antardashas)
- Allow ayanamsa selection beyond Lahiri/KP
- Add North Indian and Western wheel charts, and aspects visualization

## Disclaimer
This is for educational/demo purposes. Use authoritative libraries for real readings.
