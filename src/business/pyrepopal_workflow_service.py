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

    def _save_system_profile(self, current_session: AnalysisSessionDTO, system_info_data: Optional[Dict]) -> bool:
        logger.info(f"Attempting to save system profile for session {current_session.session_id}")
        if system_info_data and current_session.session_id is not None:
            system_profile_dto = SystemProfileDTO(
                session_id=current_session.session_id,
                profile_timestamp=datetime.utcnow().isoformat(),
                profile_data=json.dumps(system_info_data, indent=4)
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
                snapshot_data=json.dumps(repo_info_data, indent=4) # Store the whole, unadulterated object
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

    def _step_1_ingest_and_persist(self, session: AnalysisSessionDTO, repo_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Corresponds to Plan Step 1: Ingest & Persist.
        Gathers system and repository data and stores it in the database.
        """
        logger.info(f"PLAN STEP 1: Ingest & Persist for session {session.session_id}")
        system_info = self.data_collect_service.collect_system_info()
        repo_info = self.data_collect_service.collect_repository_info(repo_identifier)

        if repo_info is None:
            logger.error(f"Critical failure: Could not ingest repository data from '{repo_identifier}'.")
            session.status = "failed_repo_ingestion"
            self.analysis_session_repo.update(session)
            return None

        # Persist the ingested data
        self._save_system_profile(session, system_info)
        if not self._save_repository_snapshot(session, repo_info):
            return None # Failure status is set within the helper

        return {"system_info": system_info, "repo_info": repo_info}

    def _step_2_parse_and_prepare(self, session: AnalysisSessionDTO, ingestion_data: Dict[str, Any], template_filename: str) -> Optional[GeneratedPromptDTO]:
        """
        Corresponds to Plan Step 2: Parse & Prepare.
        Uses the ingested data to prepare and store a high-context AI prompt.
        """
        logger.info(f"PLAN STEP 2: Parse & Prepare for session {session.session_id}")
        template_content = self.data_collect_service.load_prompt_template(template_filename)
        if not template_content:
            session.status = "failed_template_load"
            self.analysis_session_repo.update(session)
            return None

        context_for_template = ingestion_data.get("repo_info", {}).copy()
        if ingestion_data.get("system_info"):
            context_for_template["system_info"] = ingestion_data["system_info"]

        prompt_str = self.data_collect_service.populate_prompt_template(template_content, context_for_template)

        saved_prompt_dto = self._save_generated_prompt(session, prompt_str, template_filename)
        return saved_prompt_dto # Returns None on failure, status set in helper

    def _step_3_deep_research(self, session: AnalysisSessionDTO, prompt_dto: GeneratedPromptDTO) -> Optional[AIAnalysisResultDTO]:
        """
        Corresponds to Plan Step 3: Deep Research.
        Sends the prepared prompt to the AI and stores the raw response.
        """
        logger.info(f"PLAN STEP 3: Deep Research for session {session.session_id}")
        ai_response_raw = self._call_ai_service(session, prompt_dto.prompt_content)
        if not ai_response_raw:
            return None # Failure status is set within the helper

        saved_ai_result_dto = self._save_ai_analysis_result(session, prompt_dto.prompt_id, ai_response_raw)
        return saved_ai_result_dto # Returns None on failure, status set in helper

    def _step_4_deliver_clarity(self, session: AnalysisSessionDTO, ai_result_dto: AIAnalysisResultDTO) -> bool:
        """
        Corresponds to Plan Step 4: Deliver Clarity.
        Parses the raw AI response into a structured, actionable format.
        """
        logger.info(f"PLAN STEP 4: Deliver Clarity for session {session.session_id}")
        
        try:
            parsed_model = self.ai_response_parser.parse_response_to_model(ai_result_dto.ai_response_raw, MinSysReqsDTO)
            ai_result_dto.parsed_system_requirements_json = parsed_model.model_dump_json(indent=4)
        except AIResponseParsingError as e:
            logger.error(f"Failed to parse AI response for session {session.session_id}, result ID {ai_result_dto.result_id}: {e}")
            session.status = "failed_ai_response_parsing"
            self.analysis_session_repo.update(session)
            return False

        try:
            updated_dto = self.ai_analysis_result_repo.update(ai_result_dto)
            if not updated_dto:
                logger.error(f"Failed to update AI analysis result with parsed data for session {session.session_id}, result ID {ai_result_dto.result_id}.")
                session.status = "failed_ai_result_update_parsed"
                self.analysis_session_repo.update(session)
                return False
        except Exception as e:
            logger.error(f"Unexpected DB error during AI result update for session {session.session_id}: {e}")
            session.status = "failed_ai_result_update_parsed" # Still an update failure
            self.analysis_session_repo.update(session)
            return False

        logger.success(f"Successfully parsed and stored structured data for session {session.session_id}.")
        return True

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
            # Execute the plan, step by step.
            ingestion_data = self._step_1_ingest_and_persist(current_session, target_repo_identifier)
            if not ingestion_data:
                return current_session

            prepared_prompt = self._step_2_parse_and_prepare(current_session, ingestion_data, prompt_template_filename)
            if not prepared_prompt:
                return current_session

            research_result = self._step_3_deep_research(current_session, prepared_prompt)
            if not research_result:
                return current_session

            clarity_achieved = self._step_4_deliver_clarity(current_session, research_result)
            if not clarity_achieved:
                return current_session

            current_session.status = "completed_successfully" # Or more granular status
            self.analysis_session_repo.update(current_session)
            logger.success(f"Repository analysis completed for session ID: {current_session.session_id}")
            return current_session

        except Exception as e:
            logger.critical(f"Unhandled exception during analysis workflow for session {current_session.session_id}: {e}")
            if current_session and current_session.session_id:
                current_session.status = "failed_exception"
                self.analysis_session_repo.update(current_session)
            return current_session