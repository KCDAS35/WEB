#Requires -Version 5.1
<#
One-shot installer + launcher for the OmniVoice local app on Windows.
Paste this one-liner into PowerShell:

    iwr -useb https://raw.githubusercontent.com/KCDAS35/WEB/refs/heads/claude/continue-previous-work-ahKnH/apps/omnivoice/install_windows.ps1 | iex

It will:
  1. Download app.py and templates/index.html into $env:USERPROFILE\WEB\apps\omnivoice
  2. Create a venv using whichever Python is on PATH
  3. Install a slim set of client-only deps (no torch, no omnivoice)
  4. Start the app and open http://localhost:8765
#>

$ErrorActionPreference = "Stop"

$Root = Join-Path $env:USERPROFILE "WEB\apps\omnivoice"
$TemplatesDir = Join-Path $Root "templates"
$Base = "https://raw.githubusercontent.com/KCDAS35/WEB/refs/heads/claude/continue-previous-work-ahKnH/apps/omnivoice"

Write-Host "[install] target folder: $Root" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TemplatesDir | Out-Null

Write-Host "[install] downloading app.py and index.html"
Invoke-WebRequest -UseBasicParsing "$Base/app.py"               -OutFile (Join-Path $Root "app.py")
Invoke-WebRequest -UseBasicParsing "$Base/templates/index.html" -OutFile (Join-Path $TemplatesDir "index.html")

Set-Location $Root

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "[install] creating Python virtual env (venv)"
    python -m venv venv
}

$Py = Join-Path $Root "venv\Scripts\python.exe"
$Pip = Join-Path $Root "venv\Scripts\pip.exe"

Write-Host "[install] upgrading pip and installing client-only deps"
& $Py -m pip install --upgrade pip --quiet
& $Pip install --quiet `
    "fastapi>=0.111" `
    "uvicorn[standard]>=0.29" `
    "python-multipart>=0.0.9" `
    "soundfile>=0.12.1" `
    "numpy>=1.26" `
    "requests>=2.31"

Write-Host "[install] opening browser in 2s..." -ForegroundColor Green
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8765"
} | Out-Null

Write-Host "[install] starting OmniVoice local app on http://localhost:8765"
Write-Host "[install] press Ctrl+C to stop the server"
& $Py "$Root\app.py"
