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

## 🔧 Testing & Debug Scripts for Automation

This application includes comprehensive testing infrastructure for validation and debugging. These scripts are designed for automation, continuous integration, and accuracy verification.

### Available Test Scripts

#### 1. **Comprehensive Test Suite (`run_test.py`)**
The main automated test runner that validates all calculations:

```powershell
python run_test.py
```

**Features:**
- Automatically starts/stops Flask app
- Tests all 9 planet positions + ascendant
- Validates against known accurate reference data
- Returns meaningful exit codes for CI/CD
- Comprehensive pass/fail reporting

**For CI/CD Automation:**
```powershell
# Exit code 0 = all tests passed, 1 = failures
python run_test.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All astronomy calculations validated"
} else {
    Write-Host "❌ Calculation accuracy issues detected"
    exit 1
}
```

#### 2. **Direct Function Testing (`test_direct.py`)**
Tests the core calculation functions without Flask overhead:

```powershell
python test_direct.py
```

**Use Cases:**
- Unit testing individual calculations
- Performance benchmarking
- Debugging calculation logic
- Regression testing after code changes

#### 3. **API Endpoint Testing (`test_api_direct.py`)**
Tests the REST API endpoints directly:

```powershell
python test_api_direct.py
```

**Features:**
- Direct HTTP API validation
- JSON response verification
- Error handling testing
- Network timeout handling

#### 4. **Specialized Debug Scripts**

**Ascendant Debugging (`debug_ascendant.py`):**
```powershell
python debug_ascendant.py
```
- Isolated ascendant calculation testing
- Step-by-step calculation verification
- Coordinate transformation validation

**Calculation Comparison (`compare_calculations.py`):**
```powershell
python compare_calculations.py
```
- Compares multiple calculation methods
- Identifies precision differences
- Validates against reference implementations

### Automation Integration Examples

#### GitHub Actions CI/CD
```yaml
name: Astronomy Accuracy Tests
on: [push, pull_request]
jobs:
  test-calculations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd astrology
          pip install -r requirements.txt
      - name: Run accuracy tests
        run: |
          cd astrology
          python run_test.py
      - name: Run unit tests
        run: |
          cd astrology
          python test_direct.py
```

#### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Test Astronomy Calculations') {
            steps {
                dir('astrology') {
                    bat 'python run_test.py'
                    bat 'python test_direct.py'
                }
            }
        }
    }
    post {
        failure {
            mail subject: 'Astronomy Calculation Tests Failed',
                 body: 'Planet position calculations are inaccurate'
        }
    }
}
```

#### Azure DevOps Pipeline
```yaml
trigger:
- main

pool:
  vmImage: 'windows-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.10'
- script: |
    cd astrology
    pip install -r requirements.txt
    python run_test.py
  displayName: 'Validate Astronomy Calculations'
```

### Test Data & Accuracy Standards

**Reference Test Case:**
- **Date**: August 22, 1996, 12:23 PM
- **Location**: Coimbatore, India (11.0118°N, 76.9628°E)
- **Timezone**: UTC+5.5
- **Ayanamsa**: Lahiri
- **Accuracy**: ±0.01° for all planetary positions

**Expected Results:**
```json
{
  "ascendant": 215.42,
  "planets": {
    "Sun": 125.63, "Moon": 217.35, "Mars": 84.37,
    "Mercury": 152.95, "Jupiter": 254.23, "Venus": 79.90,
    "Saturn": 342.62, "Rahu": 166.22, "Ketu": 346.22
  }
}
```

### Monitoring & Alerts

**For Production Monitoring:**
```powershell
# Daily accuracy check
$result = python run_test.py
if ($LASTEXITCODE -ne 0) {
    # Send alert to monitoring system
    Invoke-WebRequest -Uri "https://monitoring.example.com/alert" `
        -Method POST -Body @{
            service = "astrology-app"
            message = "Calculation accuracy degraded"
            severity = "critical"
        }
}
```

**Performance Benchmarking:**
```powershell
# Measure calculation performance
Measure-Command { python test_direct.py } | 
    Select-Object TotalMilliseconds | 
    Export-Csv "performance_metrics.csv" -Append
```

### Debugging Common Issues

**Variable Collision Detection:**
The test scripts will catch variable name collisions that can cause calculation errors:
- Geographic vs planetary longitude conflicts
- Parameter vs local variable overwrites
- String vs numeric type mismatches

**Precision Validation:**
- Tests verify calculations to 0.01° accuracy
- Detects coordinate system conversion errors
- Validates ayanamsa applications

**Integration Testing:**
- End-to-end Flask API testing
- JSON response validation
- Error handling verification

### Future Enhancements

For additional automation capabilities:
1. **Load Testing**: Scale test with multiple simultaneous calculations
2. **Regression Testing**: Archive test results for historical comparison
3. **Performance Monitoring**: Track calculation speed over time
4. **Cross-Platform Testing**: Validate across different OS/Python versions

## Disclaimer
This is for educational/demo purposes. Use authoritative libraries for real readings.
