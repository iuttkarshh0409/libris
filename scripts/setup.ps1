# setup.ps1 - Environment Setup Script

$root = Resolve-Path "$PSScriptRoot\.."
Set-Location $root

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Setting Up Libris..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Verify Python Installation
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Error "Python not found. Please install Python 3.10+ and add it to your PATH."
    exit 1
}

# 2. Verify Node.js Installation
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Error "Node.js not found. Please install Node.js (v18+ or v20+) and add it to your PATH."
    exit 1
}

# 3. Setup Backend Virtual Environment & Dependencies
Write-Host "`nSetting up backend python environment..." -ForegroundColor Green
cd backend
if (-not (Test-Path .venv)) {
    python -m venv .venv
    Write-Host "Created virtual environment." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
}

Write-Host "Activating virtual environment and installing python dependencies..." -ForegroundColor Green
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt

# Create default .env file if it doesn't exist
if (-not (Test-Path .env)) {
    New-Item -Path .env -ItemType File -Value "PORT=8000`nGEMINI_API_KEY=`nCHROMADB_PERSIST_DIR=./data/chroma`nBOOK_METADATA_DIR=./data/metadata" | Out-Null
    Write-Host "Created default .env configuration in backend directory." -ForegroundColor Green
}
cd ..

# 4. Setup Frontend Node Modules
Write-Host "`nInstalling frontend node dependencies..." -ForegroundColor Green
cd frontend
npm install
cd ..

Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE! All dependencies installed." -ForegroundColor Green
Write-Host "Run start_all.ps1 to start the platform dev servers." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
