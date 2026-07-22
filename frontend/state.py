"""Gestión centralizada de st.session_state — sin lógica de negocio."""

from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def _load_secrets() -> dict:
    """Lee API keys desde st.secrets con fallback a cadena vacía."""
    keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
    result: dict = {}
    for k in keys:
        try:
            result[k] = st.secrets.get(k, "")
        except StreamlitSecretNotFoundError:
            result[k] = ""
    try:
        result["OLLAMA_URL"] = st.secrets.get("OLLAMA_URL", "http://localhost:11434")
    except StreamlitSecretNotFoundError:
        result["OLLAMA_URL"] = "http://localhost:11434"
    return result


def inicializar_estado() -> None:
    """Inicializa todas las claves de session_state necesarias en la app."""
    st.session_state.setdefault(
        "tutor_messages",
        [
            {
                "role": "assistant",
                "content": (
                    "Hola, soy tu tutor de Ingeniería Eléctrica. "
                    "¿Qué deseas consultar sobre la asignatura seleccionada?"
                ),
            }
        ],
    )
    st.session_state.setdefault("tutor_chain", None)
    st.session_state.setdefault("tutor_chain_config", None)
    st.session_state.setdefault("tutor_config", _load_secrets())
