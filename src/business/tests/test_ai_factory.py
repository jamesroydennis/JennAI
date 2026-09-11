import pytest
from unittest.mock import MagicMock, patch

from src.business.ai.ai_factory import create_ai_service
from src.business.ai.gemini_api import AIGenerator
from src.business.ai.openai_api import OpenAIGenerator


@pytest.mark.parametrize(
    "provider, env_var, patch_target, expected_type",
    [
        ("gemini", "GOOGLE_API_KEY", "src.business.ai.gemini_api.GenerativeModel", AIGenerator),
        ("openai", "OPENAI_API_KEY", "src.business.ai.openai_api.OpenAI", OpenAIGenerator),
    ],
)
def test_create_ai_service_returns_expected_provider(provider, env_var, patch_target, expected_type, monkeypatch):
    """create_ai_service should instantiate the correct IAIService implementation per provider."""
    monkeypatch.setenv(env_var, "dummy-key")
    with patch(patch_target, return_value=MagicMock()):
        service = create_ai_service(provider=provider)
    assert isinstance(service, expected_type)


def test_create_ai_service_defaults_to_configured_provider(monkeypatch):
    """When no provider is given, create_ai_service should use config.config.AI_PROVIDER."""
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy-key")
    with patch("src.business.ai.gemini_api.GenerativeModel", return_value=MagicMock()):
        service = create_ai_service()
    assert isinstance(service, AIGenerator)


def test_create_ai_service_raises_for_unsupported_provider():
    """An unknown provider name should raise a clear ValueError."""
    with pytest.raises(ValueError, match="Unsupported AI provider"):
        create_ai_service(provider="not-a-real-provider")


def test_create_ai_service_uses_explicit_api_key_over_env(monkeypatch):
    """An explicitly passed api_key should take precedence over the environment variable."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with patch("src.business.ai.gemini_api.GenerativeModel", return_value=MagicMock()):
        service = create_ai_service(provider="gemini", api_key="explicit-key")
    assert service.api_key == "explicit-key"
