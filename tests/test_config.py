from backend.config import get_settings


def test_settings_defaults_exist(monkeypatch):
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    settings = get_settings()
    assert settings.model_name == "openrouter/google/gemini-2.5-flash"
    assert settings.openrouter_api_key == ""
    assert settings.max_files > 0
