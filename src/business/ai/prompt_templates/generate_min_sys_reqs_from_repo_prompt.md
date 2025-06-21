---
title: Generate Minimum System Requirements from Repository Information as JSON
description: |
  This prompt instructs the AI to analyze repository information (README, requirements.txt, environment.yaml, existing system requirements) and generate a JSON object representing the minimum system requirements. The JSON object MUST strictly adhere to the following schema:

  ```json
  {
    "cpu_cores": integer (required, positive),
    "ram_gb": float (required, positive),
    "storage_gb": float (required, positive),
    "operating_system": array of strings (optional),
    "dependencies": array of strings (optional),
    "notes": string (optional)
  }
  ```

  **Field Descriptions:**

  *   `cpu_cores`: Minimum number of CPU cores required. Must be a positive integer.
  *   `ram_gb`: Minimum RAM in gigabytes. Must be a positive float.
  *   `storage_gb`: Minimum free storage space in gigabytes. Must be a positive float.
  *   `operating_system`: (Optional) List of compatible operating systems (e.g., `["Windows 10", "Ubuntu 20.04"]`).
  *   `dependencies`: (Optional) List of required software or libraries (e.g., `["python>=3.9", "pytorch==2.1", "cuda==11.8"]`).
  *   `notes`: (Optional) Additional context or notes regarding the requirements.

  **Response Format:**

  Provide the system requirements as a single JSON object, enclosed in a markdown code block like this:

  ```json
  {
    "cpu_cores": 4,
    "ram_gb": 8.0,
    "storage_gb": 20.0,
    "operating_system": ["Windows 10", "Ubuntu 20.04"],
    "dependencies": ["python>=3.8", "numpy", "pandas"],
    "notes": "A dedicated GPU with at least 4GB of VRAM is highly recommended for optimal performance."
  }
  ```

  Do not include any introductory or explanatory text outside of the JSON code block. The response should be directly parsable as JSON.
---

## Instructions:

Given the following information about a software repository, determine the minimum system requirements necessary to run the software.

### Repository Information:

**README Content:**
```
{{readme_content}}
```

**requirements.txt Content:**
```
{{requirements_txt_content}}
```

**environment.yaml Content:**
```
{{environment_yaml_content}}
```

**Existing Minimum System Requirements (if available):**
```
{{existing_min_sys_reqs_content}}
```

Analyze the provided text carefully and generate the JSON output.