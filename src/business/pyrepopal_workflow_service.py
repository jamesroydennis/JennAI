# /home/jdennis/Projects/JennAI/src/business/pyrepopal_workflow_service.py

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json # For parsing AI response if it's JSON

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.loguru_setup import logger
from src.business.ai.data_collect_service import DataCollectService
from src.business.interfaces.IAIService import IAIService
# Import the new parser and its related components
from src.business.ai.ai_response_parser import AIResponseParser, AIResponseParsingError
from src.data.interfaces.ICrudRepository import ICrudRepository
from src.data.obj.analysis_session_dto import AnalysisSessionDTO
from src.data.obj.system_profile_dto import SystemProfileDTO
from src.data.obj.repository_snapshot_dto import RepositorySnapshotDTO
from src.data.obj.generated_prompt_dto import GeneratedPromptDTO
from src.data.obj.ai_analysis_result_dto import AIAnalysisResultDTO
# Import the DTO we'll be parsing into
from src.data.obj.min_sys_reqs_dto import MinSysReqsDTO

class PyRepoPalWorkflowService:
    """
    Orchestrates the PyRepo-Pal analysis workflow, including data collection,
    AI interaction, and data persistence.
    """

    def __init__(self,
                 data_collect_service: DataCollectService,
                 ai_service: IAIService,
                 ai_response_parser: AIResponseParser, # Add the parser dependency
                 analysis_session_repo: ICrudRepository[AnalysisSessionDTO],
                 system_profile_repo: ICrudRepository[SystemProfileDTO],
                 repository_snapshot_repo: ICrudRepository[RepositorySnapshotDTO],
                 generated_prompt_repo: ICrudRepository[GeneratedPromptDTO],
                 ai_analysis_result_repo: ICrudRepository[AIAnalysisResultDTO]):
        self.data_collect_service = data_collect_service
        self.ai_service = ai_service
        self.ai_response_parser = ai_response_parser
        self.analysis_session_repo = analysis_session_repo
        self.system_profile_repo = system_profile_repo
        self.repository_snapshot_repo = repository_snapshot_repo
        self.generated_prompt_repo = generated_prompt_repo
        self.ai_analysis_result_repo = ai_analysis_result_repo
        logger.info("PyRepoPalWorkflowService initialized with all dependencies.")

    def _create_initial_session(self, target_repo_identifier: str, user_notes: Optional[str]) -> Optional[AnalysisSessionDTO]:
        logger.info(f"Attempting to create initial analysis session for: {target_repo_identifier}")
        session_dto = AnalysisSessionDTO.new_session(
            target_repo_id=target_repo_identifier,
            notes=user_notes
        )
        session_dto.status = "session_created"
        created_session = self.analysis_session_repo.create(session_dto)
        if not created_session or created_session.session_id is None:
            logger.error("Failed to create and retrieve analysis session.")
            return None
        logger.info(f"Analysis session created with ID: {created_session.session_id}")
        return created_session

    def _collect_data_and_prepare_prompt(self, current_session: AnalysisSessionDTO, repo_path: str, template_filename: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Starting data collection and prompt preparation for session {current_session.session_id}")
        collection_result = self.data_collect_service.prepare_analysis_data_and_prompt(
            repo_path=repo_path,
            template_filename=template_filename
        )
        if not collection_result:
            logger.error(f"Failed to collect data or prepare prompt for session {current_session.session_id}.")
            current_session.status = "failed_data_collection"
            self.analysis_session_repo.update(current_session)
            return None
        return collection_result

    def _save_system_profile(self, current_session: AnalysisSessionDTO, system_info_data: Optional[Dict]) -> bool:
        logger.info(f"Attempting to save system profile for session {current_session.session_id}")
        if system_info_data and current_session.session_id is not None:
            # Construct the DTO directly to ensure correct field mapping
            # from the profiler's output to the DTO's attributes.
            system_profile_dto = SystemProfileDTO(
                session_id=current_session.session_id,
                profile_timestamp=datetime.utcnow().isoformat(),
                os_info=json.dumps(system_info_data.get("os")),
                cpu_info=json.dumps(system_info_data.get("cpu")),
                ram_info=json.dumps(system_info_data.get("ram")),
                gpu_info=json.dumps(system_info_data.get("gpu_info")),
                disk_info=json.dumps(system_info_data.get("disk")),
                python_info=json.dumps(system_info_data.get("python"))
            )
            saved_system_profile = self.system_profile_repo.create(system_profile_dto)
            if not saved_system_profile or saved_system_profile.profile_id is None:
                logger.warning(f"Failed to save system profile for session {current_session.session_id}.")
                # Not treating as critical failure for now
            else:
                logger.info(f"System profile saved with ID: {saved_system_profile.profile_id} for session {current_session.session_id}")
        else:
            logger.info(f"No system information collected or invalid session ID for session {current_session.session_id}, skipping profile persistence.")
        return True # Always true as it's not critical

    def _save_repository_snapshot(self, current_session: AnalysisSessionDTO, repo_info_data: Optional[Dict]) -> bool:
        logger.info(f"Attempting to save repository snapshot for session {current_session.session_id}")
        if repo_info_data is not None and current_session.session_id is not None:
            repo_snapshot_dto = RepositorySnapshotDTO(
                session_id=current_session.session_id,
                readme_content=repo_info_data.get("readme_content"),
                requirements_txt_content=repo_info_data.get("requirements_txt_content"),
                environment_yaml_content=repo_info_data.get("environment_yaml_content"),
                existing_min_sys_reqs_content=repo_info_data.get("existing_min_sys_reqs_content")
            )
            saved_repo_snapshot = self.repository_snapshot_repo.create(repo_snapshot_dto)
            if not saved_repo_snapshot or saved_repo_snapshot.snapshot_id is None:
                logger.error(f"Failed to save repository snapshot for session {current_session.session_id}. This is critical.")
                current_session.status = "failed_repo_snapshot_save"
                self.analysis_session_repo.update(current_session)
                return False
            logger.info(f"Repository snapshot saved with ID: {saved_repo_snapshot.snapshot_id} for session {current_session.session_id}")
            return True
        
        logger.error(f"No repository information available for session {current_session.session_id}.")
        current_session.status = "failed_no_repo_data_for_snapshot"
        self.analysis_session_repo.update(current_session)
        return False

    def _save_generated_prompt(self, current_session: AnalysisSessionDTO, populated_prompt_str: Optional[str], prompt_template_filename: str) -> Optional[GeneratedPromptDTO]:
        logger.info(f"Attempting to save generated prompt for session {current_session.session_id}")
        if populated_prompt_str and current_session.session_id is not None:
            generated_prompt_dto = GeneratedPromptDTO(
                session_id=current_session.session_id,
                prompt_content=populated_prompt_str,
                prompt_type="initial_analysis",
                template_name_used=prompt_template_filename,
                creation_timestamp=datetime.utcnow().isoformat()
            )
            saved_prompt_dto = self.generated_prompt_repo.create(generated_prompt_dto)
            if not saved_prompt_dto or saved_prompt_dto.prompt_id is None:
                logger.error(f"Failed to save generated prompt for session {current_session.session_id}.")
                current_session.status = "failed_prompt_save"
                self.analysis_session_repo.update(current_session)
                return None
            logger.info(f"Generated prompt saved with ID: {saved_prompt_dto.prompt_id} for session {current_session.session_id}")
            return saved_prompt_dto
        
        logger.error(f"No populated prompt string available to save for session {current_session.session_id}.")
        current_session.status = "failed_no_prompt_str_to_save"
        self.analysis_session_repo.update(current_session)
        return None

    def _call_ai_service(self, current_session: AnalysisSessionDTO, populated_prompt_str: str) -> Optional[str]:
        logger.info(f"Calling AI service for session {current_session.session_id}")
        try:
            ai_response_raw = self.ai_service.generate_text(populated_prompt_str)
            if ai_response_raw:
                logger.success(f"Successfully received AI response for session {current_session.session_id}.")
                return ai_response_raw
            
            logger.error(f"AI service returned an empty response for session {current_session.session_id}.")
            current_session.status = "failed_ai_empty_response"
            self.analysis_session_repo.update(current_session)
            return None
        except Exception as ai_ex:
            logger.error(f"Error during AI service interaction for session {current_session.session_id}: {ai_ex}")
            current_session.status = "failed_ai_interaction_exception"
            self.analysis_session_repo.update(current_session)
            return None

    def _save_ai_analysis_result(self, current_session: AnalysisSessionDTO, prompt_id: int, ai_response_raw: str) -> Optional[AIAnalysisResultDTO]:
        logger.info(f"Attempting to save AI analysis result for session {current_session.session_id}, prompt ID {prompt_id}")
        ai_analysis_result_dto = AIAnalysisResultDTO(
            prompt_id=prompt_id,
            ai_response_raw=ai_response_raw,
            response_timestamp=datetime.utcnow().isoformat()
        )
        saved_ai_result = self.ai_analysis_result_repo.create(ai_analysis_result_dto)
        if not saved_ai_result or saved_ai_result.result_id is None:
            logger.error(f"Failed to save AI analysis result for session {current_session.session_id}.")
            current_session.status = "failed_ai_result_save"
            self.analysis_session_repo.update(current_session)
            return None
        logger.info(f"AI analysis result saved with ID: {saved_ai_result.result_id} for session {current_session.session_id}")
        return saved_ai_result

    def _parse_and_update_ai_result(self, current_session: AnalysisSessionDTO, ai_result_to_update: AIAnalysisResultDTO, ai_response_raw: str) -> bool:
        logger.info(f"Attempting to parse AI response for session {current_session.session_id}, result ID {ai_result_to_update.result_id}.")
        try:
            # Use the dedicated parser to validate and structure the response
            parsed_dto = self.ai_response_parser.parse_response_to_model(ai_response_raw, MinSysReqsDTO)

            # Serialize the validated Pydantic model back to a clean, indented JSON string for storage.
            # This ensures we store a canonical, validated representation in the database.
            ai_result_to_update.parsed_system_requirements_json = parsed_dto.model_dump_json(indent=4)

            # Persist the updated DTO with the parsed JSON
            updated_dto = self.ai_analysis_result_repo.update(ai_result_to_update)
            if not updated_dto:
                logger.error(f"Failed to update AI analysis result with parsed data for session {current_session.session_id}, result ID {ai_result_to_update.result_id}.")
                current_session.status = "failed_ai_result_update_parsed"
                self.analysis_session_repo.update(current_session)
                return False

            logger.success(f"Successfully updated AI analysis result with parsed JSON for session {current_session.session_id}, result ID {ai_result_to_update.result_id}.")
            return True
        except AIResponseParsingError as e:
            logger.error(f"Failed to parse AI response for session {current_session.session_id}, result ID {ai_result_to_update.result_id}: {e}")
            current_session.status = "failed_ai_response_parsing"
            self.analysis_session_repo.update(current_session)
            return False

    def analyze_repository(self,
                           target_repo_identifier: str,
                           prompt_template_filename: str,
                           user_notes: Optional[str] = None) -> Optional[AnalysisSessionDTO]:
        """
        Main method to start and manage the repository analysis workflow.
        """
        logger.info(f"Starting repository analysis for: {target_repo_identifier}")

        current_session = self._create_initial_session(target_repo_identifier, user_notes)
        if not current_session:
            return None

        try:
            # Step 2: Collect data and prepare prompt
            collection_result = self._collect_data_and_prepare_prompt(current_session, target_repo_identifier, prompt_template_filename)
            if not collection_result:
                return current_session

            system_info_data: Optional[Dict] = collection_result.get("system_info")
            repo_info_data: Optional[Dict] = collection_result.get("repo_info")
            populated_prompt_str: Optional[str] = collection_result.get("prompt_str")

            # Step 3: Persist SystemProfile
            logger.info("Persisting collected system and repository information...")
            self._save_system_profile(current_session, system_info_data)

            # Step 4: Persist RepositorySnapshot (critical)
            if not self._save_repository_snapshot(current_session, repo_info_data):
                return current_session

            # Step 5: Persist GeneratedPrompt (critical)
            saved_prompt_dto = self._save_generated_prompt(current_session, populated_prompt_str, prompt_template_filename)
            if not saved_prompt_dto or saved_prompt_dto.prompt_id is None:
                return current_session
            prompt_id_for_ai_result = saved_prompt_dto.prompt_id

            # Step 6: Interact with AI Service
            logger.debug(f"Prompt content being sent to AI for session {current_session.session_id}:\n{populated_prompt_str}")
            logger.info("Interacting with AI service...")
            # Ensure populated_prompt_str is not None before calling, though _save_generated_prompt should have caught it
            if not populated_prompt_str: # Should be redundant if _save_generated_prompt worked
                logger.error(f"Critical error: populated_prompt_str is None before AI call for session {current_session.session_id}")
                current_session.status = "failed_internal_no_prompt_for_ai"
                self.analysis_session_repo.update(current_session)
                return current_session
            
            ai_response_raw = self._call_ai_service(current_session, populated_prompt_str)
            if not ai_response_raw:
                return current_session

            # Step 7 (Part 1): Persist raw AIAnalysisResult
            saved_ai_result_dto = self._save_ai_analysis_result(current_session, prompt_id_for_ai_result, ai_response_raw)
            if not saved_ai_result_dto:
                return current_session

            # Step 7 (Part 2): Parse AI response and update the AIAnalysisResultDTO
            if not self._parse_and_update_ai_result(current_session, saved_ai_result_dto, ai_response_raw):
                return current_session

            logger.info(f"Successfully processed and persisted AI analysis for session {current_session.session_id}.")

            current_session.status = "completed_successfully" # Or more granular status
            self.analysis_session_repo.update(current_session)
            logger.success(f"Repository analysis completed for session ID: {current_session.session_id}")
            return current_session

        except Exception as e:
            logger.error(f"Unhandled exception during analysis workflow for session {current_session.session_id}: {e}")
            if current_session and current_session.session_id:
                current_session.status = "failed_exception"
                self.analysis_session_repo.update(current_session)
            return current_session