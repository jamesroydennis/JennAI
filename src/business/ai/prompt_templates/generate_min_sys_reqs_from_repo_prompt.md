# Prompt to Determine Minimum System Requirements for a Software Repository

You are an expert system analyst AI. Your task is to analyze the provided information extracted from a software repository and determine its minimum system requirements.

## Repository Context
*(Optional: If available, provide a brief description of the repository's purpose or name. Placeholder: {{repository_description}})*

## Information Extracted from Repository Files:

### 1. Content from README.md:
```text
{{readme_content}}
```
*(If README.md was not found or is empty, this section will state: "README.md not found or empty.")*

### 2. Content from requirements.txt (if available):
```text
{{requirements_txt_content}}
```
*(If requirements.txt was not found or is empty, this section will state: "requirements.txt not found or empty.")*

### 3. Content from environment.yaml (if available):
```text
{{environment_yaml_content}}
```
*(If environment.yaml was not found or is empty, this section will state: "environment.yaml not found or empty.")*

### 4. Content from Existing Minimum System Requirements Definition (if available):
```text
{{existing_min_sys_reqs_content}}
```
*(If no existing min-sys-requirements file was found or it is empty, this section will state: "No existing min-sys-requirements file found or empty.")*

## Task:
Based on all the provided information above, please synthesize and list the minimum system requirements for this repository.
Focus on identifying requirements for the following categories if the information allows:

- **Operating System(s):** (e.g., Linux, Windows, macOS; specific versions or distributions if inferable)
- **CPU:** (e.g., minimum cores, architecture like x86_64, arm64, if inferable)
- **System RAM:** (e.g., minimum GB)
- **GPU:** (e.g., "NVIDIA GPU required", "AMD GPU required", "Any modern GPU"; minimum VRAM in GB; specific series like "NVIDIA RTX 20-series or newer"; minimum CUDA version if NVIDIA and inferable; minimum Compute Capability if inferable)
- **Disk Space:** (e.g., minimum GB for installation, dependencies, and typical datasets)
- **Python Version:** (e.g., "3.8+", "==3.9.x")
- **Key Software Dependencies or Runtimes:** (e.g., "CUDA Toolkit 11.8", "cuDNN 8.x", "Node.js 16+", specific compilers, database versions)

If information for a category is not clearly available or cannot be reasonably inferred from the provided text, please state "Not specified" or "Cannot be determined from provided information" for that category. Be cautious about making assumptions if the text is not explicit.

## Desired Output Format:
Please provide the minimum system requirements as a JSON object. Use the following keys if applicable, and add others if necessary. If a value cannot be determined, use `null` or "Not specified".

```json
{
  "operating_system": "Linux (e.g., Ubuntu 20.04+)",
  "cpu_architecture": "x86_64",
  "cpu_cores_min": 4,
  "ram_min_gb": 8,
  "gpu_required": true,
  "gpu_type_preference": "NVIDIA",
  "gpu_vram_min_gb": 6,
  "gpu_cuda_version_min": "11.8",
  "gpu_compute_capability_min": "6.1",
  "disk_space_min_gb": 50,
  "python_version_min": "3.9",
  "key_software_dependencies": ["CUDA Toolkit 11.8", "cuDNN 8.x"]
}
```

Analyze the provided text carefully and generate the JSON output.