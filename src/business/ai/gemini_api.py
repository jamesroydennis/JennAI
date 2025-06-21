# /home/jdennis/Projects/JennAI/src/business/ai/gemini_api.py

import os
from typing import Dict, Any # For options parameter
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
        self.model = GenerativeModel("gemini-1.5-flash-latest") # Use a current, valid model name
        logger.info(f"AIGenerator initialized with API Key (masked): {api_key[:5]}...")

    def generate_text(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generates text based on a given prompt and optional parameters.
        """
        logger.info(f"Generating text for prompt: '{prompt}' with options: {options}")
        # Actual API call
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_image(self, image_data: bytes, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyzes an image and returns insights.
        This method is not implemented in this specific generator.
        """
        logger.warning("analyze_image is not implemented in AIGenerator.")
        raise NotImplementedError("analyze_image is not implemented in this AIGenerator.")
