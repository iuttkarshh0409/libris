# start_frontend.ps1 - React Frontend Startup

$root = Resolve-Path "$PSScriptRoot\.."
Set-Location $root

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Starting Vite Frontend Server..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd frontend

# Run frontend dev server
Write-Host "Running frontend on http://localhost:5173..." -ForegroundColor Green
npm run dev
cd ..
