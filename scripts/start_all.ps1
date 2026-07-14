# start_all.ps1 - Launcher for both servers

$root = Resolve-Path "$PSScriptRoot\.."
Set-Location $root

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Launching Platform Servers..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Start Backend in a separate window
Write-Host "Launching backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; & 'scripts/start_backend.ps1'"

# 2. Start Frontend in a separate window
Write-Host "Launching frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; & 'scripts/start_frontend.ps1'"

Write-Host "`nBoth servers have been launched in separate windows." -ForegroundColor Green
Write-Host "---------------------------------------------" -ForegroundColor Cyan
Write-Host "FastAPI API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Vite React UI:     http://localhost:5173/" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Green
