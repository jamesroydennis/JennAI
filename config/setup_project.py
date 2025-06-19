import os
from pathlib import Path

# --- Configuration ---
# This script should be run from the JennAI project root.
# It tries to automatically detect the root.
SCRIPT_DIR = Path(__file__).resolve().parent # This will be .../JennAI/config
JENNAI_ROOT = SCRIPT_DIR.parent # This will now correctly be .../JennAI

# Fallback check (useful if script is ever run from outside expected hierarchy)
if not (JENNAI_ROOT / 'main.py').exists():
    print(f"Warning: Could not automatically detect JennAI root from {SCRIPT_DIR}. Assuming current working directory is root: {Path.cwd()}")
    JENNAI_ROOT = Path.cwd()

print(f"Detected JennAI Root: {JENNAI_ROOT}")

# --- Directory Structure ---
# Directories to create, ensuring parent directories are created first.
# This list explicitly covers all directories in your provided structure.
DIRECTORIES_TO_CREATE = [
    # "admin", # Don't create 'admin' if you keep it separate and uncommitted
    "config",
    "logs", # Main logs directory
    "core",
    "project",
    "project/business",
    "project/business/config",
    "project/business/logs",
    "project/business/notebooks",
    "project/business/tests",
    "project/data",
    "project/data/implementations",
    "project/data/interfaces",
    "project/data/logs",
    "project/data/notebooks",
    "project/data/obj",
    "project/presentation",
    "project/presentation/config",
    "project/presentation/logs",
    "project/presentation/notebooks",
    "project/presentation/tests",
    "tests", # Main tests directory
]

# --- Boilerplate Files with Content ---
# Keys are file paths relative to JENNAI_ROOT.
# Values are the content for the file. Use empty string for just creating the file.
# IMPORTANT: Files listed here will be (re)created with this content.
# Ensure you use triple quotes for multiline strings.

FILE_CONTENTS = {
    # Top Level Files
    "__init__.py": "# Top-level package for JennAI\n",
    "main.py": """# /home/jdennis/Projects/JennAI/main.py

import sys
import os
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Monorepo Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows all sub-projects (project/data, project/business, etc.)
# and centralized modules (config, core) to be imported using absolute paths.
jennai_root = Path(__file__).resolve().parent
if str(jennai_root) not in sys.path:
    sys.path.append(str(jennai_root))

# --- Centralized Core Imports ---
# These modules are now directly discoverable from the JennAI root
from config.loguru_setup import setup_logging
from config.config import DEBUG_MODE
from core.dependency_container import DependencyContainer

# --- Global Setup (Orchestrated by main.py) ---
setup_logging(debug_mode=DEBUG_MODE) # Initialize Loguru for the entire monorepo
from loguru import logger # Import the configured logger instance

logger.info(f"INFO - JennAI Monorepo Main: Orchestration initialized.")
logger.info(f"INFO - Python interpreter: {sys.executable}")
logger.info(f"INFO - Current working directory: {os.getcwd()}")
logger.info(f"INFO - JennAI project root added to PATH: {jennai_root}")
logger.info(f"INFO - Running in DEBUG_MODE: {DEBUG_MODE}")

# --- Dependency Configuration Functions for Sub-Projects ---
# These functions will be defined in main.py to configure specific sub-project dependencies.


def configure_project_business_dependencies(container: DependencyContainer):
    \"\"\"
    Configures dependencies specific to the `project/business` layer.
    \"\"\"
    logger.info("INFO - Configuring project/business dependencies (conceptual).")
    # Example: AI services like AIGenerator will be registered here.
    # from project.business.gemini_api import AIGenerator
    # container.register(AIGenerator, lambda: AIGenerator(api_key=os.getenv("GOOGLE_API_KEY")))
    logger.success("SUCCESS - project/business dependencies configured (conceptual).")

def configure_project_presentation_dependencies(container: DependencyContainer):
    \"\"\"
    Configures dependencies specific to the `project/presentation` layer.
    \"\"\"
    logger.info("INFO - Configuring project/presentation dependencies (conceptual).")
    # This will include Flask app setup later.
    logger.success("SUCCESS - project/presentation dependencies configured (conceptual).")

# --- Main Application Execution Block ---
if __name__ == '__main__':
    global_container = DependencyContainer()

    logger.info("INFO - JennAI OS is booting up and configuring core services...")

    configure_project_business_dependencies(global_container)
    configure_project_presentation_dependencies(global_container)


    logger.success("SUCCESS - JennAI OS has successfully booted and performed initial checks. Vibe coding initiated!")
""",
    "environment.yaml": """name: jennai-root
channels:
  - pytorch
  - nvidia
  - conda-forge
  - defaults

dependencies:
  - python=3.9 # Or your specific Python version
  - pip
  - pip:
    # PyTorch and related with CUDA 11.8 (Pip install)
    - "torch==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118"
    - "torchvision==0.22.1+cu118 --index-url https://download.pytorch.org/whl/cu118"
    - "torchaudio==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118"
    # Other pip dependencies (pinned for reproducibility)
    - google-generativeai==0.8.5
    - loguru==0.7.3
    - pytest==8.4.1
    - numexpr==2.10.2
    - opencv-python==4.10.0.84
""",
    "LICENSE": """MIT License

Copyright (c) 2025 James Dennis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "pyproject.toml": """# pyproject.toml - For pytest and other project configuration

[tool.pytest.ini_options]
testpaths = [
    "tests",
]
addopts = [
    "--import-mode=importlib",
    "-v",
]
markers = [
    "cuda: marks tests that require CUDA/GPU",
    "integration: marks integration tests",
]
""",
    # Config directory files
    "config/__init__.py": "# Initializes the config package.\n",
    "config/config.py": """# /home/jdennis/Projects/JennAI/config/config.py
import os

DEBUG_MODE = True
# Example: Placeholder for API Key (use environment variable in real app!)
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_FALLBACK_API_KEY_FOR_DEV_IF_NEEDED")
""",
    "config/gemini_api.py": """# /home/jdennis/Projects/JennAI/config/gemini_api.py

import os
# from google.generativeai import GenerativeModel # Uncomment when ready to use actual API

class AIGenerator:
    \"\"\"
    Conceptual class to represent interaction with a Generative AI model like Gemini.
    \"\"\"
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key must be provided for AIGenerator.")
        self.api_key = api_key
        # self.model = GenerativeModel("gemini-pro") # Uncomment when ready to use actual API
        print(f"AIGenerator initialized with API Key (masked): {api_key[:5]}...")

    def generate_content(self, prompt: str) -> str:
        \"\"\"Generates content based on a prompt (conceptual).\"\"\"
        print(f"Generating content for prompt: '{prompt}'...")
        # response = self.model.generate_content(prompt) # Uncomment for actual API call
        # return response.text
        return "Generated content (placeholder)."
""",
    "config/loguru_setup.py": """# /home/jdennis/Projects/JennAI/config/loguru_setup.py

import os
import sys
from pathlib import Path
from loguru import logger

def setup_logging(log_file_name: str = "jennai.log", debug_mode: bool = True):
    \"\"\"
    Sets up the global Loguru logger configuration.
    Removes default handlers and adds a file handler and a console handler.

    Args:
        log_file_name (str): The name of the log file (e.g., "jennai.log").
        debug_mode (bool): If True, sets level to DEBUG; otherwise, INFO.
    \"\"\"
    logger.remove()

    log_level = "DEBUG" if debug_mode else "INFO"

    logger.add(sys.stderr, level=log_level, format="{time} {level} {message}", filter="jennai")

    # Corrected: Determine the JennAI project root from loguru_setup.py's location
    current_script_dir = Path(__file__).resolve().parent # This is .../JennAI/config
    jennai_root_path = current_script_dir.parent # This is .../JennAI

    log_dir = jennai_root_path / 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = log_dir / log_file_name

    logger.add(str(log_file_path), rotation="10 MB", level=log_level, compression="zip", retention="10 days")

    logger.info(f"INFO - Loguru setup complete. Logging to file: {log_file_path}. Running in {log_level} mode.")
""",
    # Core directory files
    "core/__init__.py": "# Initializes the core package.\n",
    "core/dependency_container.py": """# /home/jdennis/Projects/JennAI/core/dependency_container.py

import inspect
from typing import Type, TypeVar, Dict, Callable, Any, Union, get_origin, get_args
from loguru import logger

# Define a TypeVar for the interface type for cleaner type hinting
I = TypeVar('I')

class DependencyContainer:
    \"\"\"
    A simple Inversion of Control (IoC) container for dependency injection.
    Allows registering concrete implementations for interfaces/abstractions,
    and resolving instances with their dependencies automatically.
    Supports singletons and pre-registered instances.
    \"\"\"
    def __init__(self):
        self._registrations: Dict[Any, Any] = {} # Key can be Type or (Origin, Args)
        self._singletons: Dict[Any, Any] = {}    # Stores instantiated singletons (keyed by abstraction key)
        logger.debug("DEBUG - DependencyContainer initialized.")

    def _get_key(self, abstraction: Type[I]) -> Any:
        \"\"\"Internal helper to get the key for registration/resolution, handling generics.\"\"\"
        if get_origin(abstraction):
            return (get_origin(abstraction), get_args(abstraction))
        return abstraction

    def register(self, abstraction: Type[I], concrete_impl: Union[Type[I], Callable[..., I]]):
        \"\"\"
        Registers a concrete implementation class or a factory function for an abstraction.
        Instances will be new on each resolve (transient lifecycle), unless registered as singleton.
        \"\"\"
        key = self._get_key(abstraction)
        self._registrations[key] = concrete_impl
        logger.debug(f"DEBUG - Registered {concrete_impl.__name__ if hasattr(concrete_impl, '__name__') else str(concrete_impl)} for {str(abstraction)} as transient.")

    def register_singleton(self, abstraction: Type[I], concrete_impl: Union[Type[I], Callable[..., I]] = None):
        \"\"\"
        Registers a concrete implementation or a factory function for an abstraction as a singleton.
        The instance will be created on the first resolve and reused for subsequent resolves.
        If concrete_impl is None, assumes abstraction is also the concrete implementation.
        \"\"\"
        key = self._get_key(abstraction)
        if concrete_impl is None:
            concrete_impl = abstraction # Assume abstraction is also the concrete class

        self._registrations[key] = concrete_impl
        # If it's a direct instance, store it immediately. Otherwise, it's lazy.
        if not inspect.isclass(concrete_impl) and not callable(concrete_impl):
            self._singletons[key] = concrete_impl
            logger.debug(f"DEBUG - Registered {str(concrete_impl)} for {str(abstraction)} as singleton (instance).")
        else:
            # Mark it as a singleton registration for lazy instantiation
            self._registrations[key] = {'type': 'singleton', 'impl': concrete_impl}
            logger.debug(f"DEBUG - Registered {concrete_impl.__name__ if hasattr(concrete_impl, '__name__') else str(concrete_impl)} for {str(abstraction)} as singleton (lazy).")

    def register_instance(self, abstraction: Type[I], instance: I):
        \"\"\"
        Registers a pre-existing instance for an abstraction. This instance will always be returned.
        \"\"\"
        key = self._get_key(abstraction)
        self._registrations[key] = instance
        self._singletons[key] = instance # Treat pre-registered instance as a singleton
        logger.debug(f"DEBUG - Registered pre-existing instance {str(instance)} for {str(abstraction)}.")

    def resolve(self, abstraction: Type[I]) -> I:
        \"\"\"
        Resolves an instance of the requested abstraction, injecting its dependencies.
        \"\"\"
        key = self._get_key(abstraction)

        # 1. Check if it's already a resolved singleton instance
        if key in self._singletons:
            logger.debug(f"DEBUG - Resolving existing singleton for {str(abstraction)}.")
            return self._singletons[key]

        # 2. Look up registration
        if key not in self._registrations:
            logger.error(f"ERROR - No implementation registered for abstraction: {str(abstraction)}.")
            raise ValueError(f"No implementation registered for abstraction: {str(abstraction)}")

        registration_entry = self._registrations[key]

        # 3. Handle singleton registration (lazy instantiation)
        is_singleton_registration = isinstance(registration_entry, dict) and registration_entry.get('type') == 'singleton'
        concrete_impl_or_factory = registration_entry['impl'] if is_singleton_registration else registration_entry

        # 4. Handle factory function
        if callable(concrete_impl_or_factory) and not inspect.isclass(concrete_impl_or_factory):
            logger.debug(f"DEBUG - Resolving {str(abstraction)} using a factory function.")
            instance = concrete_impl_or_factory()
            if is_singleton_registration: # Store result if it was marked as a singleton factory
                self._singletons[key] = instance
                logger.debug(f"DEBUG - Stored factory-resolved instance for singleton {str(abstraction)}.")
            return instance

        # 5. Handle concrete class (auto-inject dependencies)
        concrete_class = concrete_impl_or_factory
        signature = inspect.signature(concrete_class.__init__)
        dependencies = {}

        for name, param in signature.parameters.items():
            if name == 'self':
                continue

            if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD or \
               param.kind == inspect.Parameter.KEYWORD_ONLY:

                if param.annotation == inspect.Parameter.empty:
                    logger.warning(f"WARNING - Parameter '{name}' in {concrete_class.__name__}.__init__ has no type hint. Cannot auto-resolve.")
                    continue

                logger.debug(f"DEBUG - Resolving dependency '{name}' of type {str(param.annotation)} for {concrete_class.__name__}.")
                dependencies[name] = self.resolve(param.annotation) # Recursive resolution

        instance = concrete_class(**dependencies)
        logger.debug(f"DEBUG - Instantiated {concrete_class.__name__}.")

        if is_singleton_registration: # Store newly created instance if marked as singleton class
            self._singletons[key] = instance
            logger.debug(f"DEBUG - Stored newly created instance for singleton {str(abstraction)}.")

        return instance

    def reset(self):
        \"\"\"Clears all registrations and singletons.\"\"\"
        self._registrations.clear()
        self._singletons.clear()
        logger.debug("DEBUG - DependencyContainer reset.")
""",
    # Project directory files - __init__.py files for package structure
    "project/__init__.py": "# Top-level project package.\n",
    "project/business/__init__.py": "# Initializes the project.business package.\n",
    "project/business/config/__init__.py": "# Initializes project.business.config package.\n",
    "project/business/logs/__init__.py": "# Initializes project.business.logs package.\n",
    "project/business/notebooks/__init__.py": "# Initializes project.business.notebooks package.\n",
    "project/business/tests/__init__.py": "# Initializes project.business.tests package.\n",
    "project/data/__init__.py": "# Initializes the project.data package.\n",
    "project/data/implementations/__init__.py": "# Initializes project.data.implementations package.\n",
    "project/data/interfaces/__init__.py": "# Initializes project.data.interfaces package.\n",
    "project/data/logs/__init__.py": "# Initializes project.data.logs package.\n",
    "project/data/notebooks/__init__.py": "# Initializes project.data.notebooks package.\n",
    "project/data/obj/__init__.py": "# Initializes project.data.obj package.\n",
    "project/presentation/__init__.py": "# Initializes the project.presentation package.\n",
    "project/presentation/config/__init__.py": "# Initializes project.presentation.config package.\n",
    "project/presentation/logs/__init__.py": "# Initializes project.presentation.logs package.\n",
    "project/presentation/notebooks/__init__.py": "# Initializes project.presentation.notebooks package.\n",
    "project/presentation/tests/__init__.py": "# Initializes project.presentation.tests package.\n",
    "project/presentation/universe.html": "", # Empty HTML file
    "project/presentation/universe.html.short": "", # Empty HTML file

    # Tests directory files
    "tests/__init__.py": "# Initializes the tests package.\n",
    "tests/test_cuda.py": """# /home/jdennis/Projects/JennAI/tests/test_cuda.py

import torch
import pytest

# This part runs when you execute the script directly (e.g., 'python tests/test_cuda.py')
if __name__ == '__main__':
    print(f"Is CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA is NOT available. Tests requiring CUDA will likely fail.")


# This is a pytest test function
def test_cuda_device_available():
    \"\"\"
    Tests if a CUDA-enabled GPU device is available and can be accessed by PyTorch.
    \"\"\"
    assert torch.cuda.is_available(), "CUDA is not available or not detected by PyTorch!"

    if torch.cuda.is_available():
        print(f"\\n[Test] CUDA device count: {torch.cuda.device_count()}")
        print(f"[Test] CUDA device name: {torch.cuda.get_device_name(0)}")
"""
}

# --- Script Execution ---
def create_project_structure():
    print("Starting JennAI project structure creation...")

    # Create directories
    for d in DIRECTORIES_TO_CREATE:
        path = JENNAI_ROOT / d
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")

    # Create files with content
    for file_path_str, content in FILE_CONTENTS.items():
        path = JENNAI_ROOT / file_path_str
        # Ensure parent directory exists before writing file
        os.makedirs(path.parent, exist_ok=True)

        # Determine if we should overwrite:
        # Overwrite if file doesn't exist OR if it's a known boilerplate file that we want to keep updated
        should_overwrite = not path.exists() or \
                           file_path_str in [
                               "main.py",
                               "environment.yaml",
                               "pyproject.toml",
                               "config/config.py",
                               "config/gemini_api.py",
                               "config/loguru_setup.py",
                               "core/dependency_container.py",
                               "tests/test_cuda.py",
                               "boilerplate.ipynb", # Ensure the notebook always gets updated content
                               "config/setup_project.py", # IMPORTANT: This script itself should be updated
                               "admin/Project_Cleanup.ps1" # This file should be updated if moved back
                           ]

        if should_overwrite:
            with open(path, "w") as f:
                f.write(content)
            print(f"Created/Updated file: {path}")
        else:
            print(f"Skipped existing file (not a core boilerplate): {path}")

    # Optional: Git initialization - user might do this manually
    # if not (JENNAI_ROOT / '.git').exists():
    #     print("Initializing Git repository (run 'git init' manually)...")

    print("JennAI project structure creation complete!")

if __name__ == "__main__":
    create_project_structure()
