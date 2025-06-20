# /home/jdennis/Projects/JennAI/src/business/sys/sys_profiler.py

import platform
import psutil
import json
import os
import sys
from pathlib import Path
import subprocess

# --- Root Project Path Setup ---
# This allows the script to be potentially integrated with JennAI's logging/config
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent # Up to src, business, sys, then JennAI
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

try:
    from config.loguru_setup import setup_logging
    from loguru import logger
    # Setup logging for this script.
    if not logger._core.handlers: # Check if logger is already configured
        setup_logging(debug_mode=True, log_file_name="sys_profiler.log")
except ImportError:
    print("Warning: Loguru logging not initialized. Falling back to print statements.")
    class PrintLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
    logger = PrintLogger()


OUTPUT_DIR = jennai_root_for_path / "src" / "data" / "system_info"
OUTPUT_FILENAME = "hardware_specs.json"

def get_os_info():
    logger.debug("Gathering OS information...")
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }

def get_cpu_info():
    logger.debug("Gathering CPU information...")
    try:
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "max_frequency_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else None,
            "current_frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "usage_percent": psutil.cpu_percent(interval=1),
        }
    except Exception as e:
        logger.warning(f"Could not retrieve full CPU info using psutil: {e}")
        return {"error": str(e)}

def get_ram_info():
    logger.debug("Gathering RAM information...")
    try:
        svmem = psutil.virtual_memory()
        return {
            "total_gb": round(svmem.total / (1024**3), 2),
            "available_gb": round(svmem.available / (1024**3), 2),
            "used_gb": round(svmem.used / (1024**3), 2),
            "percentage_used": svmem.percent,
        }
    except Exception as e:
        logger.warning(f"Could not retrieve RAM info using psutil: {e}")
        return {"error": str(e)}

def get_disk_info(path_to_check: str = "."):
    logger.debug(f"Gathering disk information for path: {Path(path_to_check).resolve()}")
    try:
        disk_usage_path = Path(path_to_check).resolve()
        if not disk_usage_path.exists():
            logger.warning(f"Path {disk_usage_path} for disk usage check does not exist. Using current directory.")
            disk_usage_path = Path(".").resolve()
            
        disk_usage = psutil.disk_usage(str(disk_usage_path))
        return {
            "path_checked": str(disk_usage_path),
            "total_gb": round(disk_usage.total / (1024**3), 2),
            "used_gb": round(disk_usage.used / (1024**3), 2),
            "free_gb": round(disk_usage.free / (1024**3), 2),
            "percentage_used": disk_usage.percent,
        }
    except Exception as e:
        logger.warning(f"Could not retrieve disk info for '{path_to_check}' using psutil: {e}")
        return {"path_checked": path_to_check, "error": str(e)}

def get_gpu_info():
    logger.debug("Gathering GPU information...")
    gpus = []
    system_driver_version = None
    try:
        import pynvml
        pynvml.nvmlInit()
        system_driver_version = pynvml.nvmlSystemGetDriverVersion().decode()
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode()
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            try:
                major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                compute_capability = f"{major}.{minor}"
            except pynvml.NVMLError_NotSupported:
                compute_capability = "N/A (Not Supported by NVML)"
            except Exception as e_cc:
                compute_capability = f"N/A (Error: {e_cc})"

            gpus.append({
                "id": i,
                "name": name,
                "total_vram_gb": round(mem_info.total / (1024**3), 2),
                "free_vram_gb": round(mem_info.free / (1024**3), 2),
                "used_vram_gb": round(mem_info.used / (1024**3), 2),
                "compute_capability": compute_capability,
            })
        pynvml.nvmlShutdown()
    except ImportError:
        logger.warning("pynvml not installed. GPU information will be limited or unavailable.")
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free,memory.used,compute_cap", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            if lines and len(lines[0].split(',')) > 1: # Check if line is not empty and has enough parts
                system_driver_version = lines[0].split(',')[1].strip() 
            for i, line in enumerate(lines):
                if not line.strip(): continue # Skip empty lines
                parts = [p.strip() for p in line.split(',')]
                gpus.append({
                    "id": i,
                    "name": parts[0] if len(parts) > 0 else "N/A",
                    "total_vram_gb": round(int(parts[2]) / 1024, 2) if len(parts) > 2 and parts[2] != "[N/A]" and parts[2].isdigit() else "N/A",
                    "free_vram_gb": round(int(parts[3]) / 1024, 2) if len(parts) > 3 and parts[3] != "[N/A]" and parts[3].isdigit() else "N/A",
                    "used_vram_gb": round(int(parts[4]) / 1024, 2) if len(parts) > 4 and parts[4] != "[N/A]" and parts[4].isdigit() else "N/A",
                    "compute_capability": parts[5] if len(parts) > 5 and parts[5] != "[N/A]" else "N/A (from nvidia-smi)",
                })
        except FileNotFoundError:
            logger.error("nvidia-smi command not found. Cannot retrieve GPU information.")
        except subprocess.CalledProcessError as e:
            logger.error(f"nvidia-smi command failed: {e.stderr}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while trying to use nvidia-smi: {e}")
    except pynvml.NVMLError as e:
        logger.error(f"NVML Error: {e}. Ensure NVIDIA drivers are installed and running.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during GPU info gathering: {e}")

    return {"nvidia_driver_version": system_driver_version, "gpus": gpus}

def get_python_info():
    logger.debug("Gathering Python environment information...")
    return {
        "version": sys.version,
        "executable": sys.executable,
        "conda_env": os.getenv("CONDA_DEFAULT_ENV"),
        "conda_prefix": os.getenv("CONDA_PREFIX"),
    }

def main():
    logger.info("Starting system profiling (PyRepo-Pal)...")

    disk_check_path = jennai_root_for_path

    system_info = {
        "os": get_os_info(),
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "disk": get_disk_info(str(disk_check_path)),
        "gpu_info": get_gpu_info(),
        "python": get_python_info(),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file_path = OUTPUT_DIR / OUTPUT_FILENAME

    try:
        with open(output_file_path, "w") as f:
            json.dump(system_info, f, indent=4)
        logger.success(f"System information successfully saved to: {output_file_path}")
    except IOError as e:
        logger.error(f"Failed to write system information to {output_file_path}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while saving system info: {e}")

if __name__ == "__main__":
    main()