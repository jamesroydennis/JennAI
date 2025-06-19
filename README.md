# JennAI Project

This is the main repository for the JennAI project, structured as a monorepo
to manage different aspects of the application including business logic,
data handling, and presentation layers.

## Project Structure

- `admin/`: Administrative scripts (cleanup, folder creation, regression runner).
- `config/`: Configuration files and logging setup.
- `core/`: Core utilities like the dependency injection container.
- `logs/`: Default directory for log files.
- `src/`: Contains the main application source code:
  - `src/business/`: Business logic, AI services.
  - `src/data/`: Data access layers, repositories.
  - `src/presentation/`: UI, API endpoints, static/template files.
- `tests/`: Top-level integration and system tests.

## Setup

1. Ensure you have Conda installed.
2. Create the Conda environment from the `environment.yaml` file:
   ```bash
   conda env create -f environment.yaml
   ```
3. Activate the environment:
   ```bash
   conda activate jennai-root
   ```

## Running Tests

```bash
pytest
```

## Regression Testing Workflow

For ensuring project stability after significant changes, the following workflow is recommended.

**Automated Workflow:**

The easiest way to run the full regression suite is using the provided shell script:
```bash
bash admin/run_regression.sh
```
This script will perform all the steps below and exit with an appropriate status code. (Note: Ensure the script has execute permissions: `chmod +x admin/run_regression.sh`)

**Manual Steps (if not using the script):**

1.  **Clean Project Artifacts**:
    Remove cached files and display the current project tree.
    ```bash
    python admin/cleanup.py
    ```

2.  **Run Automated Tests**:
    Execute all unit and integration tests. Test-specific logs are written to `logs/pytest.log`.
    ```bash
    pytest
    ```

3.  **Check Logs for Errors**:
    Scan the `pytest.log` file for any critical error patterns. This script will exit with a non-zero status code if errors are found.
    ```bash
    python admin/check_logs.py logs/pytest.log
    ```
    You can also use `python admin/check_logs.py logs/jennai.log` to scan the main application log if it was run independently.