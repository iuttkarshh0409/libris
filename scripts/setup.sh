#!/usr/bin/env bash
# setup.sh - Environment Setup Script for macOS/Linux

set -e

echo "============================================="
echo "Setting Up Libris..."
echo "============================================="

# 1. Verify Python
if command -v python3 &>/dev/null; then
    echo "Found Python: $(python3 --version)"
elif command -v python &>/dev/null; then
    echo "Found Python: $(python --version)"
else
    echo "Error: Python 3 not found. Please install Python 3.10+." >&2
    exit 1
fi

# 2. Verify Node
if command -v node &>/dev/null; then
    echo "Found Node.js: $(node --version)"
else
    echo "Error: Node.js not found. Please install Node.js (v18+ or v20+)." >&2
    exit 1
fi

# 3. Setup Backend Virtual Environment & Dependencies
echo ""
echo "Setting up backend python environment..."
cd backend

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created virtual environment."
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment and installing python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create default .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "PORT=8000\nGEMINI_API_KEY=\nCHROMADB_PERSIST_DIR=./data/chroma\nBOOK_METADATA_DIR=./data/metadata" > .env
    echo "Created default .env configuration in backend directory."
fi
cd ..

# 4. Setup Frontend Node Modules
echo ""
echo "Installing frontend node dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "============================================="
echo "SETUP COMPLETE! All dependencies installed."
echo "Run scripts/start_all.ps1 or start manually."
echo "============================================="
