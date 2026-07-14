# Lint and Formatting Checker for Libris
# Runs Ruff & mypy on backend, Oxlint & Prettier on frontend.

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Running Backend Lint Checks (Ruff)..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd backend
.venv\Scripts\ruff check src tests
$ruffCheckResult = $LASTEXITCODE

Write-Host "Checking Backend Formatting (Ruff format)..." -ForegroundColor Cyan
.venv\Scripts\ruff format --check src tests
$ruffFormatResult = $LASTEXITCODE

Write-Host "Checking Backend Types (mypy)..." -ForegroundColor Cyan
.venv\Scripts\mypy src tests
$mypyResult = $LASTEXITCODE
cd ..

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Running Frontend Lint & Format Checks..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

cd frontend
npm run lint
$frontendLintResult = $LASTEXITCODE
cd ..

Write-Host "=============================================" -ForegroundColor Cyan
$failed = $false
if ($ruffCheckResult -ne 0) { Write-Host "Backend Ruff check failed." -ForegroundColor Red; $failed = $true }
if ($ruffFormatResult -ne 0) { Write-Host "Backend Ruff format check failed." -ForegroundColor Red; $failed = $true }
if ($mypyResult -ne 0) { Write-Host "Backend mypy type check failed." -ForegroundColor Red; $failed = $true }
if ($frontendLintResult -ne 0) { Write-Host "Frontend lint/format check failed." -ForegroundColor Red; $failed = $true }

if (-not $failed) {
    Write-Host "SUCCESS: All lint and formatting checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAILURE: Some lint/format checks failed." -ForegroundColor Red
    exit 1
}
