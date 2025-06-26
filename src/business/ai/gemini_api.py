import os
from typing import Dict, Any, Optional
from loguru import logger
from google.generativeai import GenerativeModel # Ensure this is uncommented
from src.business.interfaces.IAIService import IAIService # Import the interface

class AIGenerator(IAIService): # Inherit from IAIService
    """
    Concrete implementation of IAIService using a Gemini-like model.
    """
    def __init__(self, api_key: str):
        if not api_key:
            logger.error("API key must be provided for AIGenerator.")
            raise ValueError("API key must be provided for AIGenerator.")
        self.api_key = api_key
        self.model = GenerativeModel("gemini-pro") # Initialize the model
        logger.info(f"AIGenerator initialized with API Key (masked): {api_key[:5]}...")

    def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates text based on a given prompt and optional parameters.
        """
        logger.info(f"Generating text for prompt: '{prompt}' with options: {options}")
        # Actual API call
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_image(self, image_data: bytes, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes an image and returns insights.
        This method is not implemented in this specific generator.
        """
        logger.warning("analyze_image is not implemented in AIGenerator.")
        raise NotImplementedError("analyze_image is not implemented in this AIGenerator.")
