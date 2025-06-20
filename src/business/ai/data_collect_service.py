# data_collect_service.py

import sys
import json
from pathlib import Path
from typing import Dict, Optional

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

try:
    from config.loguru_setup import setup_logging
    from loguru import logger
    if not logger._core.handlers:
        setup_logging(debug_mode=True, log_file_name="data_collect_service.log")
except ImportError:
    print("Warning: Loguru logging not initialized for DataCollectService. Falling back to print statements.")
    class PrintLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
    logger = PrintLogger()

# Import other necessary modules from the project
from src.business.sys import sys_profiler
from src.business.ai import repo_data_collector

class DataCollectService:
    """
    Service to collect data from various sources (system, repository),
    populate a prompt template with this data, and persist the generated prompt.
    """
    def __init__(self):
        self.project_root = jennai_root_for_path
        self.sys_info_dir = self.project_root / "src" / "data" / "system_info"
        self.sys_info_file = self.sys_info_dir / sys_profiler.OUTPUT_FILENAME
        self.prompt_template_dir = self.project_root / "src" / "business" / "ai" / "prompt_templates"
        self.generated_prompts_dir = self.project_root / "src" / "data" / "generated_prompts"

        # Ensure output directories exist
        self.generated_prompts_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"DataCollectService initialized. Generated prompts will be saved to: {self.generated_prompts_dir}")

    def _collect_system_info(self) -> Optional[Dict]:
        """
        Runs the system profiler and reads its output.
        Returns the system information as a dictionary, or None on failure.
        """
        logger.info("Collecting system information...")
        try:
            # Run the sys_profiler's main function to generate/update the hardware_specs.json
            sys_profiler.main() # Assumes sys_profiler.main() is callable and handles its own errors
            
            if self.sys_info_file.exists():
                with open(self.sys_info_file, 'r', encoding='utf-8') as f:
                    system_data = json.load(f)
                logger.success(f"Successfully loaded system information from {self.sys_info_file}")
                return system_data
            else:
                logger.error(f"System information file not found after running profiler: {self.sys_info_file}")
                return None
        except Exception as e:
            logger.error(f"Failed to collect or load system information: {e}")
            return None

    def _collect_repository_info(self, repo_path_str: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Collects repository information using repo_data_collector.
        Returns repository data as a dictionary, or None on failure.
        """
        logger.info(f"Collecting repository information from: {repo_path_str}")
        try:
            repo_data = repo_data_collector.collect_repository_data(repo_path_str)
            if repo_data.get("error") and "Invalid repository path" in repo_data["error"]: # Check specific error message
                logger.error(f"Repository data collection failed: {repo_data['error']}")
                return None
            logger.success(f"Successfully collected repository information from: {repo_path_str}")
            return repo_data
        except Exception as e:
            logger.error(f"Failed to collect repository information: {e}")
            return None

    def _load_prompt_template(self, template_filename: str) -> Optional[str]:
        """Loads a prompt template file."""
        template_file_path = self.prompt_template_dir / template_filename
        logger.info(f"Loading prompt template: {template_file_path}")
        if template_file_path.is_file():
            try:
                template_content = template_file_path.read_text(encoding='utf-8')
                logger.success(f"Successfully loaded template: {template_filename}")
                return template_content
            except Exception as e:
                logger.error(f"Could not read template file {template_file_path}: {e}")
                return None
        logger.error(f"Prompt template file not found: {template_file_path}")
        return None

    def _populate_prompt_template(self, template_content: str, data_context: Dict[str, Optional[str]]) -> str:
        """Populates the prompt template with collected data.
        Placeholders in the template should be like {{key_name}}.
        """
        logger.info("Populating prompt template...")
        import re # For finding placeholders

        # Initialize populated_data with defaults for all known placeholders.
        populated_data = {
            "readme_content": "README.md not found or empty.",
            "requirements_txt_content": "requirements.txt not found or empty.",
            "environment_yaml_content": "environment.yaml not found or empty.",
            "existing_min_sys_reqs_content": "No existing min-sys-requirements file found or empty.",
            "repository_description": "No repository description provided."
            # Add any other placeholders from your primary template with their defaults here
        }

        # Override defaults with actual values from data_context if they exist and are not None.
        # Also, add any "unexpected" keys from data_context.
        if data_context:
            for key, value in data_context.items():
                if value is not None: # If data_context has a real value, use it
                    populated_data[key] = value
                # If value is None, the default from populated_data (if key is known) will be kept.
                # If key is new and value is None, we'll handle it below by checking all template placeholders.

        populated_prompt = template_content
        
        # Find all placeholders in the template like {{placeholder_name}}
        placeholders_in_template = set(re.findall(r"{{(.*?)}}", template_content))

        for key in placeholders_in_template:
            value_to_substitute = populated_data.get(key)
            if value_to_substitute is None: # If key not in populated_data or its value was None after previous step
                value_to_substitute = f"{key} not found or empty." # Generic default for any other placeholder
            populated_prompt = populated_prompt.replace(f"{{{{{key}}}}}", str(value_to_substitute))
        
        logger.success("Prompt template populated.")
        return populated_prompt

    def _save_generated_prompt(self, prompt_content: str, output_filename: str) -> Optional[Path]:
        """Saves the generated prompt to a file."""
        output_file_path = self.generated_prompts_dir / output_filename
        logger.info(f"Saving generated prompt to: {output_file_path}")
        try:
            output_file_path.write_text(prompt_content, encoding='utf-8')
            logger.success(f"Prompt successfully saved: {output_file_path}")
            return output_file_path
        except Exception as e:
            logger.error(f"Failed to save prompt to {output_file_path}: {e}")
            return None

    def generate_and_save_repo_analysis_prompt(self, repo_path: str, template_filename: str, output_prompt_filename: str) -> Optional[Path]:
        """Orchestrates the collection, template population, and saving of a prompt."""
        logger.info(f"Starting generation of repo analysis prompt for: {repo_path}")
        
        # Step 1: Collect data sources
        # System info is collected but not directly used in the current primary prompt template.
        self._collect_system_info() 
        
        repo_data = self._collect_repository_info(repo_path)
        if not repo_data: 
            logger.warning("Repository data collection returned None or an error state. Aborting prompt generation.")
            return None

        # Step 2: Receive (load) a template
        template_content = self._load_prompt_template(template_filename)
        if not template_content: return None

        # Step 3: Convert collected data into that template
        context_for_template = repo_data.copy() # Start with repo_data
        # Example of merging other data sources if needed by the template:
        # system_info_data = self._collect_system_info()
        # if system_info_data:
        #     context_for_template.update(system_info_data)
            
        populated_prompt = self._populate_prompt_template(template_content, context_for_template)

        # Step 4: Persist the prompt
        saved_path = self._save_generated_prompt(populated_prompt, output_prompt_filename)
        return saved_path

if __name__ == "__main__":
    logger.info("DataCollectService - Standalone Run Example")
    service = DataCollectService()

    # Use the sample repository we created
    sample_repo_path = str(service.project_root / "src" / "data" / "sample")
    target_template = "generate_min_sys_reqs_from_repo_prompt.md"
    output_filename = "sample_repo_analysis_prompt.txt"

    # Ensure the sample repo path is valid before proceeding
    if not Path(sample_repo_path).is_dir():
        logger.error(f"Sample repository path does not exist or is not a directory: {sample_repo_path}")
        logger.error("Please ensure the sample data is correctly set up in src/data/sample/")
    else:
        generated_prompt_path = service.generate_and_save_repo_analysis_prompt(
            repo_path=sample_repo_path,
            template_filename=target_template,
            output_prompt_filename=output_filename
        )

        if generated_prompt_path:
            logger.info(f"Example prompt generated and saved to: {generated_prompt_path}")
            logger.info("You can now inspect this file.")
        else:
            logger.error("Failed to generate and save the example prompt.")
