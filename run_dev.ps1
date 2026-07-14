# Development Server Launcher for Libris
# Run this script to start both backend and frontend development servers.

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Starting Libris Dev Servers..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Start Backend in a background job or separate process
Write-Host "Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .venv\Scripts\python -m uvicorn src.main:app --reload --port 8000"

# 2. Start Frontend in a background job or separate process
Write-Host "Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Both servers have been launched in separate terminal windows." -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend App: http://localhost:5173" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
