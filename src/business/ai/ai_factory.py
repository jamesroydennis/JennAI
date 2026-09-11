"""
Factory for creating IAIService implementations based on a configurable
AI provider, so the application is not hardcoded to a single AI vendor.

The provider can be selected via the `AI_PROVIDER` environment variable
(see `config.config.AI_PROVIDER`), e.g. "gemini" or "openai". Each provider
resolves its API key from the environment variable configured in
`config.config.AI_PROVIDERS`.
"""
import os
from typing import Optional

from loguru import logger

from config.config import AI_PROVIDER, AI_PROVIDERS
from src.business.interfaces.IAIService import IAIService


def create_ai_service(provider: Optional[str] = None, api_key: Optional[str] = None) -> IAIService:
    """
    Creates and returns an IAIService implementation for the requested provider.

    Args:
        provider: Name of the AI provider to use (e.g. "gemini", "openai").
            Defaults to the `AI_PROVIDER` setting from config.config.
        api_key: API key to use for the provider. Defaults to the value of
            the provider's configured environment variable.

    Returns:
        An IAIService implementation for the selected provider.

    Raises:
        ValueError: If the provider is unsupported or no API key is available.
    """
    provider = (provider or AI_PROVIDER).lower()

    if provider not in AI_PROVIDERS:
        supported = ", ".join(sorted(AI_PROVIDERS.keys()))
        logger.error(f"Unsupported AI provider: '{provider}'. Supported providers: {supported}.")
        raise ValueError(f"Unsupported AI provider: '{provider}'. Supported providers: {supported}.")

    if api_key is None:
        api_key = os.getenv(AI_PROVIDERS[provider]["api_key_env"])

    logger.info(f"Creating AI service for provider: '{provider}'.")

    if provider == "gemini":
        from src.business.ai.gemini_api import AIGenerator
        return AIGenerator(api_key=api_key)

    if provider == "openai":
        from src.business.ai.openai_api import OpenAIGenerator
        return OpenAIGenerator(api_key=api_key)

    # Should be unreachable due to the AI_PROVIDERS membership check above.
    raise ValueError(f"Unsupported AI provider: '{provider}'.")
