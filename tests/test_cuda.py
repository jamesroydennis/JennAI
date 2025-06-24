import torch
import pytest
import sys
import subprocess


def get_nvidia_smi_output():
    """Attempts to run nvidia-smi and returns its output for diagnostics."""
    try:
        result = subprocess.run(
            "nvidia-smi", capture_output=True, text=True, shell=True, check=False
        )
        if result.returncode == 0:
            return result.stdout
        return f"Could not execute 'nvidia-smi'. Is it in your PATH?\nError:\n{result.stderr}"
    except FileNotFoundError:
        return "'nvidia-smi' command not found. Is the NVIDIA driver installed correctly?"
    except Exception as e:
        return f"An unexpected error occurred while running 'nvidia-smi': {e}"


def test_cuda_is_core_requirement():
    """
    Validates that the system's core requirement, a CUDA-enabled GPU, is
    available and correctly configured for PyTorch.

    This test will FAIL if CUDA is not detected, providing detailed diagnostics
    to help resolve the environment/setup issue.
    """
    if torch.cuda.is_available():
        print("\n--- CUDA Environment Details ---")
        print(f"PyTorch Version: {torch.__version__}")
        print(f"PyTorch CUDA Version: {torch.version.cuda}")
        print(f"Detected CUDA Devices: {torch.cuda.device_count()}")
        print(f"Current Device: {torch.cuda.get_device_name(torch.cuda.current_device())}")
        print("--- Test Passed ---")
        assert True, "SUCCESS: CUDA is available and configured."
        return

    # --- Diagnostics for Failure ---
    failure_message = (
        f"\n\n{'='*20} CUDA SETUP VALIDATION FAILED {'='*20}\n"
        "CRITICAL: This project requires a correctly configured CUDA environment.\n"
        "Do NOT skip this test. Use the diagnostics below to fix the system setup.\n\n"
        "--- System & PyTorch Diagnostics ---\n"
        f"1. Python Interpreter: {sys.executable}\n"
        f"2. PyTorch Version: {torch.__version__}\n"
        f"3. PyTorch Compiled with CUDA Version: {torch.version.cuda or 'Not built with CUDA support'}\n"
        f"4. torch.cuda.is_available() returned: False\n\n"
        "--- NVIDIA Driver Diagnostics ---\n"
        f"5. `nvidia-smi` command output:\n"
        f"{'-'*40}\n{get_nvidia_smi_output()}\n{'-'*40}\n\n"
        "--- Troubleshooting Steps ---\n"
        "A. Check `nvidia-smi`: If it fails or shows errors, your NVIDIA drivers are not installed correctly.\n"
        "B. Check Conda Environment: Ensure 'jennai-root' is active. Run `conda list` and verify `pytorch-cuda` matches your driver's CUDA version.\n"
        "C. Recreate Environment: A full reset via `full_reset.bat` can resolve inconsistencies.\n"
    )
    pytest.fail(failure_message, pytrace=False)
