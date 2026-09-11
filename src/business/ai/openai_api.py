from typing import Dict, Any, Optional
from loguru import logger
from openai import OpenAI
from src.business.interfaces.IAIService import IAIService


class OpenAIGenerator(IAIService):
    """
    Concrete implementation of IAIService using the OpenAI API.
    """
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        if not api_key:
            logger.error("API key must be provided for OpenAIGenerator.")
            raise ValueError("API key must be provided for OpenAIGenerator.")
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
        logger.info(f"OpenAIGenerator initialized with API Key (masked): {api_key[:5]}...")

    def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates text based on a given prompt and optional parameters.
        """
        logger.info(f"Generating text for prompt: '{prompt}' with options: {options}")
        options = options or {}
        response = self.client.chat.completions.create(
            model=options.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def analyze_image(self, image_data: bytes, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes an image and returns insights.
        This method is not implemented in this specific generator.
        """
        logger.warning("analyze_image is not implemented in OpenAIGenerator.")
        raise NotImplementedError("analyze_image is not implemented in this OpenAIGenerator.")
