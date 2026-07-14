# demo.ps1 - Run the End-to-End Pipeline Demo

$root = Resolve-Path "$PSScriptRoot\.."
Set-Location $root

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Running End-to-End RAG Demonstration..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Start Backend if not already running
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$startedServer = $false
$backendProc = $null

if (-not $portProcess) {
    Write-Host "Backend server is not active on port 8000. Launching temporary instance..." -ForegroundColor Yellow
    cd backend
    $backendProc = Start-Process powershell -ArgumentList "-Command", ".venv\Scripts\python -m uvicorn src.main:app --port 8000" -PassThru -WindowStyle Hidden
    $startedServer = $true
    cd ..
    Write-Host "Waiting 5 seconds for FastAPI initialization..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "Using active backend server instance on port 8000." -ForegroundColor Green
}

# 2. Run the E2E Flow Script
Write-Host "`nExecuting verification flow runner..." -ForegroundColor Green
python run_e2e_flow.py
$demoResult = $LASTEXITCODE

# 3. Clean up if we launched the temporary backend
if ($startedServer -and $backendProc) {
    Write-Host "`nShutting down temporary backend instance (PID: $($backendProc.Id))..." -ForegroundColor Yellow
    Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "`n=============================================" -ForegroundColor Cyan
if ($demoResult -eq 0) {
    Write-Host "DEMO COMPLETE: All verification stages succeeded!" -ForegroundColor Green
} else {
    Write-Host "DEMO FAILED: One or more integration stages failed." -ForegroundColor Red
}
Write-Host "=============================================" -ForegroundColor Cyan
