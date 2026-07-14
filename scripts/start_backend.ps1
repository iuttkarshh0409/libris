# start_backend.ps1 - FastAPI Backend Startup

$root = Resolve-Path "$PSScriptRoot\.."
Set-Location $root

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI Backend Server..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd backend

# Stop any running process on port 8000
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portProcess) {
    Write-Host "Found existing process on port 8000. Stopping it..." -ForegroundColor Yellow
    Stop-Process -Id $portProcess[0].OwningProcess -Force
}

# Run backend
Write-Host "Running backend on http://localhost:8000..." -ForegroundColor Green
.venv\Scripts\python -m uvicorn src.main:app --port 8000 --reload
cd ..
