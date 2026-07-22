"""Fábrica de modelos de chat con interfaz unificada por proveedor."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

PROVIDER_MODELS: dict[str, list[str]] = {
    "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    "Google": ["gemini-2.0-flash", "gemini-1.5-pro"],
    "Ollama": ["qwen3.5:4b", "llama3.1:8b"],
}


def get_llm(
    provider: str,
    model: str,
    api_key: str | None = None,
    ollama_url: str | None = None,
) -> BaseChatModel:
    """Retorna una instancia `BaseChatModel` según proveedor y modelo."""
    if provider not in PROVIDER_MODELS:
        raise ValueError(f"Proveedor no soportado: {provider}")
    if model not in PROVIDER_MODELS[provider]:
        raise ValueError(f"Modelo no permitido para {provider}: {model}")

    if provider == "OpenAI":
        if not api_key:
            raise ValueError("Debes proporcionar una API key de OpenAI.")
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, api_key=api_key, temperature=0.2)

    if provider == "Anthropic":
        if not api_key:
            raise ValueError("Debes proporcionar una API key de Anthropic.")
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model, api_key=api_key, temperature=0.2)

    if provider == "Google":
        if not api_key:
            raise ValueError("Debes proporcionar una API key de Google.")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.2)

    from langchain_ollama import ChatOllama

    return ChatOllama(model=model, base_url=ollama_url or "http://localhost:11434", temperature=0.2)
