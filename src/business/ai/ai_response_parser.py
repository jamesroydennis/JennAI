# /home/jdennis/Projects/JennAI/src/business/ai/ai_response_parser.py
import sys
import json
import re
from pathlib import Path
from typing import Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.loguru_setup import logger

# Create a generic type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)

class AIResponseParsingError(Exception):
    """Custom exception for errors during AI response parsing."""
    pass

class AIResponseParser:
    """
    A service dedicated to parsing and validating raw text responses from an AI
    into structured Pydantic models.
    """

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extracts a JSON object from a string, robustly handling cases where
        it's embedded in markdown code blocks or surrounded by other text.
        """
        if not text:
            return None

        # Pattern to find JSON within ```json ... ``` markdown block
        # re.DOTALL allows '.' to match newlines
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            logger.debug("Found JSON in a markdown code block.")
            return match.group(1)

        # If no markdown block, try to find the first '{' and last '}'
        try:
            start_index = text.index('{')
            end_index = text.rindex('}') + 1
            potential_json = text[start_index:end_index]
            json.loads(potential_json) # Quick validation
            logger.debug("Found JSON by locating the outer curly braces.")
            return potential_json
        except (ValueError, json.JSONDecodeError):
            logger.warning("Could not find a valid JSON object in the text.")
            return None

    def parse_response_to_model(self, response_text: str, model_class: Type[T]) -> T:
        """
        Parses a raw AI response string into a specified Pydantic model instance.
        """
        logger.debug(f"Attempting to parse response into {model_class.__name__}.")
        
        json_str = self._extract_json_from_text(response_text)
        if not json_str:
            raise AIResponseParsingError("Could not extract a valid JSON object from the AI response text.")

        try:
            parsed_model = model_class.model_validate_json(json_str)
            logger.success(f"Successfully parsed and validated AI response into {model_class.__name__}.")
            return parsed_model
        except ValidationError as e:
            raise AIResponseParsingError(f"AI response JSON does not match the expected schema. Details: {e}")
        except json.JSONDecodeError as e:
            raise AIResponseParsingError(f"The extracted text is not valid JSON. Details: {e}")