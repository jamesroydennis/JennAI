# JennAI Project

This is the main repository for the JennAI project, structured as a monorepo
to manage different aspects of the application including business logic,
data handling, and presentation layers.

## Project Structure

- `admin/`: Administrative scripts (cleanup, folder creation, regression runner).
- `config/`: Configuration files and logging setup.
- `core/`: Core utilities like the dependency injection container.
- `logs/`: Default directory for log files.
  - `jennai.log`: Logs from the main application (`main.py`) and admin scripts.
  - `pytest_session.log`: Logs generated specifically during `pytest` test runs.
- `src/`: Contains the main application source code:
  - `src/business/`: Business logic, AI services.
  - `src/data/`: Data access layers, repositories.
  - `src/presentation/`: UI, API endpoints, static/template files.
- `tests/`: Top-level integration and system tests.

## Setup

To get the JennAI project running, follow these steps:

1.  **Install Conda**: Ensure you have Conda (Miniconda or Anaconda) installed.

2.  **Create and Activate Conda Environment**:
    Create the Conda environment from the `environment.yaml` file:
    ```bash
    conda env create -f environment.yaml
    ```
    Activate the environment:
    ```bash
    conda activate jennai-root
    ```
    This environment includes essential Python packages like `pytest`, `loguru`, `pytest-loguru`, and `allure-pytest`.

3.  **Install Java Development Kit (JDK)**:
    The Allure reporting tool requires Java. Install a JDK (version 8 or higher is typically sufficient).
    *   **Recommended:** Use a package manager (e.g., `brew install openjdk` on macOS, `sudo apt install default-jdk` on Ubuntu, `scoop install java` on Windows).
    *   **Alternatively:** Download from Adoptium (OpenJDK) or Oracle.
    Ensure the `java` command is available in your system's PATH and the `JAVA_HOME` environment variable is set.

4.  **Install Allure Command-line Tool**:
 (This step is for Allure reporting, which is part of the automated regression workflow)
    This tool is needed to generate and view Allure reports.
    *   **Recommended:** Use a package manager (e.g., `brew install allure` on macOS, `scoop install allure` on Windows, or `npm install -g allure-commandline` if you have Node.js/npm).
    *   **Alternatively:** Download the zip/tgz from the Allure GitHub releases page and add its `/bin` directory to your system's PATH.

## Running Tests

To run tests and generate Allure reports, see the Regression Testing Workflow below. For a quick test run without full reporting, you can use:
```bash
pytest
```
All structured logs (from Pytest, application, admin scripts) will be written to `logs/jennai.log`.

## Regression Testing Workflow

For ensuring project stability after significant changes, the following workflow is recommended.

**Automated Workflow:**

The easiest way to run the full regression suite is using the provided shell script:
```bash
bash admin/run_regression.sh
```
This script will:
1. Clean project artifacts (including previous Allure results and log files).
2. Run `pytest` and generate raw Allure result data.
3. Generate an HTML Allure report from the results.
4. Open the Allure report in your web browser.
5. Exit with an appropriate status code based on test outcomes.

(Note: Ensure the script has execute permissions: `chmod +x admin/run_regression.sh`. You also need the Allure command-line tool installed and in your PATH, which requires Java.)

**Manual Steps (if not using the script):**

1.  **Clean Project Artifacts**:
    Remove cached files, previous Allure results, and old log files.
    ```bash
    python admin/cleanup.py
    ```

2.  **Run Automated Tests**:
    Execute all unit and integration tests and generate Allure result data.
    ```bash
    pytest --alluredir=allure-results
    ```

3.  **Generate and View Allure Report**:
    Process the raw results to create an HTML report and open it.
    ```bash
    allure generate allure-results -o allure-report --clean
    allure open allure-report
    ```