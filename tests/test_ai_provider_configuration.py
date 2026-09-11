import pytest

from src.business.ai.gemini_api import AIGenerator


def test_ai_generator_uses_configured_api_resource(monkeypatch):
    captured = {}

    class DummyModel:
        def __init__(self, model_name):
            captured["model_name"] = model_name

    monkeypatch.setattr("src.business.ai.gemini_api.GenerativeModel", DummyModel)

    generator = AIGenerator(
        api_key="test-key",
        provider="gemini",
        api_resource="gemini-2.5-flash",
    )

    assert generator.provider == "gemini"
    assert generator.api_resource == "gemini-2.5-flash"
    assert captured["model_name"] == "gemini-2.5-flash"


def test_ai_generator_rejects_unsupported_provider():
    with pytest.raises(ValueError, match="Unsupported AI provider"):
        AIGenerator(api_key="test-key", provider="openai", api_resource="gpt-4o")
