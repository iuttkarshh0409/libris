# format_all.ps1 - Run backend and frontend formatters

$root = Resolve-Path "$PSScriptRoot\.."
Set-Location $root

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Formatting Backend Code (Ruff)..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd backend
.venv\Scripts\ruff format src tests
cd ..

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "Formatting Frontend Code (Prettier)..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd frontend
npm run format
cd ..

Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "SUCCESS: All files successfully formatted!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
