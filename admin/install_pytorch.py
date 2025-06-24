import subprocess
import sys

def install_pytorch():
    """
    Installs the specific CUDA 11.8-enabled version of PyTorch, torchvision, and torchaudio.
    
    This script is intended to be run *after* the conda environment has been created,
    as a separate, explicit step to ensure the correct GPU-enabled binaries are installed
    from the specified PyTorch index URL.
    """
    command = [
        sys.executable,  # Use the same python interpreter that is running this script
        "-m",
        "pip",
        "install",
        "torch==2.7.1+cu118",
        "torchvision==0.22.1+cu118",
        "torchaudio==2.7.1+cu118",
        "--index-url",
        "https://download.pytorch.org/whl/cu118"
    ]

    print("======================================================================")
    print("==           INSTALLING PYTORCH WITH CUDA 11.8 SUPPORT            ==")
    print("======================================================================")
    print(f"Running command: {' '.join(command)}")
    print("This may take several minutes and require a large download...")
    print("-" * 70)

    try:
        # Using subprocess.run to execute the command.
        # We stream the output directly to the console by not capturing stdout/stderr,
        # which gives the user real-time feedback from pip.
        subprocess.run(command, check=True)
        print("-" * 70)
        print("✅ PyTorch installation completed successfully.")
        print("======================================================================")
    except subprocess.CalledProcessError as e:
        print("-" * 70)
        print(f"❌ ERROR: PyTorch installation failed with exit code {e.returncode}.")
        print("Please check the output above for specific error messages from pip.")
        print("Ensure you have a compatible NVIDIA driver and CUDA setup on your host machine.")
        print("======================================================================")
        sys.exit(1) # Exit with a non-zero code to indicate failure

if __name__ == "__main__":
    install_pytorch()