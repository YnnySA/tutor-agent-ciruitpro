"""Componente sidebar del Tutor RAG — selector de asignatura, proveedor y modelo."""

from __future__ import annotations

import yaml
from pathlib import Path

import streamlit as st
from backend.llm_factory import get_provider_models

ROOT = Path(__file__).resolve().parent.parent


def _load_asignaturas() -> dict[str, str]:
    """Retorna {nombre_display: collection_id} desde config/asignaturas.yaml."""
    config_path = ROOT / "config" / "asignaturas.yaml"
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)["asignaturas"]
    return {v["nombre_display"]: k for k, v in data.items()}


def _load_providers_meta() -> dict:
    config_path = ROOT / "config" / "providers.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)["providers"]


def render_sidebar() -> dict:
    """
    Renderiza el sidebar y retorna la configuración activa:
    {asignatura, provider, model, api_key, ollama_url}
    """
    asignaturas = _load_asignaturas()
    provider_models = get_provider_models()
    providers_meta = _load_providers_meta()
    config = st.session_state["tutor_config"]

    with st.sidebar:
        st.subheader("Configuración del tutor")

        asignatura_label = st.selectbox("Asignatura", list(asignaturas.keys()))
        asignatura = asignaturas[asignatura_label]

        provider = st.selectbox("Proveedor LLM", list(provider_models.keys()))
        model = st.selectbox("Modelo", provider_models[provider])

        api_key = ""
        ollama_url = config.get("OLLAMA_URL", "http://localhost:11434")

        if provider == "Ollama":
            st.info("Para Ollama no se requiere API key.")
            ollama_url = st.text_input(
                "URL de Ollama",
                value=ollama_url,
                key="sidebar_ollama_url",
                help="Ejemplo: http://localhost:11434",
            )
            config["OLLAMA_URL"] = ollama_url
        else:
            key_env = providers_meta[provider].get("key_env", "")
            api_key = st.text_input(
                f"API key de {provider}",
                type="password",
                value=config.get(key_env, ""),
                key=f"sidebar_api_key_{provider.lower()}",
            )
            if api_key:
                config[key_env] = api_key

    return {
        "asignatura": asignatura,
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "ollama_url": ollama_url,
    }
