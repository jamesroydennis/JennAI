from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class IAIService(ABC):
    """
    Interface (Abstract Base Class) for AI services.
    Defines the contract for operations related to AI functionalities
    like text generation, image analysis, etc.
    """

    @abstractmethod
    def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates text based on a given prompt and optional parameters.

        Args:
            prompt: The input text prompt for the AI model.
            options: A dictionary of additional options for generation (e.g., temperature, max_tokens).

        Returns:
            The generated text as a string.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_image(self, image_data: bytes, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes an image and returns insights.

        Args:
            image_data: The image data in bytes.
            options: A dictionary of additional options for analysis.

        Returns:
            A dictionary containing the analysis results.
        """
        raise NotImplementedError