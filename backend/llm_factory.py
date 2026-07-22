"""Fábrica de modelos de chat con interfaz unificada por proveedor."""

from __future__ import annotations

import yaml
from pathlib import Path
from langchain_core.language_models import BaseChatModel


def _load_providers() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "config" / "providers.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)["providers"]


def get_provider_models() -> dict[str, list[str]]:
    """Retorna dict {proveedor: [modelos]} leído desde config/providers.yaml."""
    return {k: v["modelos"] for k, v in _load_providers().items()}


# Alias compatible con el frontend existente
PROVIDER_MODELS: dict[str, list[str]] = get_provider_models()


def get_llm(
    provider: str,
    model: str,
    api_key: str | None = None,
    ollama_url: str | None = None,
) -> BaseChatModel:
    """Retorna una instancia BaseChatModel según proveedor y modelo."""
    providers = _load_providers()
    if provider not in providers:
        raise ValueError(f"Proveedor no soportado: {provider}")
    if model not in providers[provider]["modelos"]:
        raise ValueError(f"Modelo no permitido para {provider}: {model}")

    temp = 0.2
    cfg = providers[provider]

    if provider == "OpenAI":
        if not api_key:
            raise ValueError("Debes proporcionar una API key de OpenAI.")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=api_key, temperature=temp)

    if provider == "Anthropic":
        if not api_key:
            raise ValueError("Debes proporcionar una API key de Anthropic.")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, api_key=api_key, temperature=temp)

    if provider == "Google":
        if not api_key:
            raise ValueError("Debes proporcionar una API key de Google.")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=temp)

    from langchain_ollama import ChatOllama
    default_url = cfg.get("default_url", "http://localhost:11434")
    return ChatOllama(model=model, base_url=ollama_url or default_url, temperature=temp)
