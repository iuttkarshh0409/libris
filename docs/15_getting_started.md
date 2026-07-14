# Getting Started Guide

Welcome to **Libris** developer onboarding guide. This guide will help you set up your local development environment and run your first document query in under 10 minutes.

---

## 1. Prerequisites

Before installing, ensure your machine meets the following environment requirements:
- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+ recommended)
- **Git**: Version 2.20 or newer
- **Python**: Version `3.10` or `3.11` (specifically tested on `3.11`)
- **Node.js**: Version `18.x` or `20.x` (LTS versions)
- **Package Managers**: `npm` (bundled with Node) and `poetry` or `pip` (Python package managers)

---

## 2. Environment Setup

Follow these step-by-step instructions to configure both the backend and frontend components.

### Python Installation & Virtual Environment
If you don't have Python installed, download it from the official [Python Downloads page](https://www.python.org/downloads/) (tick the box "Add Python to PATH" on Windows).

1. **Verify Python Installation**:
   ```bash
   python --version
   ```
2. **Navigate to the Backend Directory**:
   ```bash
   cd backend
   ```
3. **Create a Virtual Environment**:
   *Using standard venv:*
   ```bash
   python -m venv .venv
   ```
4. **Activate the Virtual Environment**:
   *   **Windows (PowerShell)**:
       ```powershell
       .venv\Scripts\Activate.ps1
       ```
   *   **macOS / Linux (Bash/Zsh)**:
       ```bash
       source .venv/bin/activate
       ```
5. **Install Dependencies**:
   We use poetry or pip. To install packages with pip:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Node.js & Frontend Installation
1. **Verify Node.js Installation**:
   ```bash
   node --version
   npm --version
   ```
2. **Navigate to the Frontend Directory**:
   ```bash
   cd ../frontend
   ```
3. **Install Node Dependencies**:
   ```bash
   npm install
   ```

---

## 3. Environment Variables

The backend requires configuration variables to locate model files, database directories, and manage LLM fallback states.

1. Create a `.env` file in the `backend/` directory.
2. Add the following environment properties:

```env
# Server Port (default is 8000)
PORT=8000

# Google Gemini API Key (Optional)
# If left empty, the provider automatically falls back to a smart local simulation.
GEMINI_API_KEY=your_gemini_api_key_here

# Local Directory Paths
CHROMADB_PERSIST_DIR=./data/chroma
BOOK_METADATA_DIR=./data/metadata
```

> [!NOTE]
> If `GEMINI_API_KEY` is not provided, the platform functions normally using simulated academic responses, ensuring developer environment stability out of the box.

---

## 4. First Launch

You can launch both servers simultaneously using our provided utility scripts or run them manually in separate shells:

### Running Manually

1. **Start the FastAPI Backend**:
   Navigate to the `backend/` directory, ensure the virtual environment is active, and run:
   ```bash
   python -m uvicorn src.main:app --port 8000 --reload
   ```
   You should see `Uvicorn running on http://127.0.0.1:8000`.

2. **Start the React/Vite Frontend**:
   Navigate to the `frontend/` directory and run:
   ```bash
   npm run dev
   ```
   Vite will start the server on `http://localhost:5173`. Open this URL in your web browser.

---

## 5. First Query

Follow these steps to ingest a textbook and submit your first search:

1. **Upload a Textbook**:
   - Open `http://localhost:5173/library` in your browser.
   - Click **Ingest New Book** and select a valid academic PDF (e.g., `computer_networks.pdf` from the root of this project).
   - Wait for the pipeline status indicator to transition from `queued` to `completed`.
2. **Submit a Query**:
   - Navigate to the **Query Workspace** page.
   - select the newly ingested book from the **Scope Textbook** dropdown.
   - Type your academic question (e.g. `What are the seven layers of the OSI model?`).
   - Press `Ctrl+Enter` or click **Submit**.
   - Review the compiled answer, clickable citation highlights, and embedding similarity metrics in the RAG Execution Diagnostics panel.

---

## 6. Troubleshooting

### 1. Address Already in Use (Error 10048 / EADDRINUSE)
*   **Reason**: Another process is already running on port `8000` (FastAPI) or `5173` (Vite).
*   **Fix**:
    *   **Windows**:
        ```powershell
        Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
        ```
    *   **macOS / Linux**:
        ```bash
        kill -9 $(lsof -t -i:8000)
        ```

### 2. PyPDF Missing or PDF Parsing Errors
*   **Reason**: The uploaded PDF is scanned (contains images instead of selectable text) or corrupted.
*   **Fix**: Ensure your textbook contains native text layers. If parsing fails, try validating with another PDF or regenerating the sample textbook using `python generate_textbook.py`.

### 3. ChromaDB SQLite3 Version Outdated (Linux)
*   **Reason**: ChromaDB requires SQLite version `3.35.0` or higher.
*   **Fix**: Update your sqlite3 binary or install `pysqlite3-binary` and override standard sqlite3 via system environment:
    ```bash
    pip install pysqlite3-binary
    ```
    And import it at the top of your backend's entrypoint.
