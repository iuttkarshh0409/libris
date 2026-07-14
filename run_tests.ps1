# Test Runner for Libris
# Runs both backend (pytest) and frontend (vitest) tests.

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Running Backend Tests (pytest)..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd backend
.venv\Scripts\pytest
$backendResult = $LASTEXITCODE
cd ..

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Running Frontend Tests (vitest)..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd frontend
npm run test
$frontendResult = $LASTEXITCODE
cd ..

Write-Host "=============================================" -ForegroundColor Cyan
if ($backendResult -eq 0 -and $frontendResult -eq 0) {
    Write-Host "SUCCESS: All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAILURE: Some tests failed." -ForegroundColor Red
    Write-Host "Backend Exit Code: $backendResult" -ForegroundColor Yellow
    Write-Host "Frontend Exit Code: $frontendResult" -ForegroundColor Yellow
    exit 1
}
