# Contributing Guidelines

Thank you for your interest in contributing to **Libris**! We welcome bug reports, documentation updates, feature requests, and pull requests.

---

## 1. Code of Conduct
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.

---

## 2. Development Workflow

1.  **Fork the Repository**: Create a personal fork on GitHub.
2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/libris.git
    cd libris
    ```
3.  **Run Environment Setup**:
    *   **Windows**:
        ```powershell
        ./scripts/setup.ps1
        ```
    *   **macOS / Linux**:
        ```bash
        ./scripts/setup.sh
        ```
4.  **Create a Feature Branch**:
    ```bash
    git checkout -b feature/my-amazing-feature
    ```
5.  **Write Code & Implement Features**:
    *   Ensure your implementation adheres to the project's **Clean Architecture** conventions (see [Developer Guide](docs/16_developer_guide.md)).
6.  **Run Formatters and Linters**:
    Make sure your modifications pass all code quality checks:
    ```powershell
    ./scripts/format_all.ps1
    ./scripts/lint_all.ps1
    ```
7.  **Run Tests**:
    Verify that all tests continue to pass 100%:
    ```powershell
    ./scripts/test_all.ps1
    ```
8.  **Commit Changes**:
    Write clear, descriptive git commit messages:
    ```bash
    git commit -m "feat(generation): add new LLM provider model config"
    ```
9.  **Push and Open a Pull Request (PR)**:
    Push to your fork and submit a PR to the main branch of this repository.

---

## 3. Creating New Providers

If you are adding a new Vector Database provider or LLM provider, follow the abstract base patterns defined in the contracts. See [docs/16_developer_guide.md](docs/16_developer_guide.md) for a step-by-step example.
