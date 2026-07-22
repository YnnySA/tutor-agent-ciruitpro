"""Página para configurar credenciales y URL de Ollama."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Configuración", page_icon=":material/settings:")
st.title("Configuración del tutor")
st.caption("Guarda tus credenciales de proveedores y la URL de Ollama")

st.session_state.setdefault(
    "tutor_config",
    {
        "openai_api_key": "",
        "anthropic_api_key": "",
        "google_api_key": "",
        "ollama_url": "http://localhost:11434",
    },
)

config = st.session_state["tutor_config"]

with st.form("configuracion_llm"):
    openai_api_key = st.text_input(
        "API key de OpenAI",
        value=config.get("openai_api_key", ""),
        type="password",
    )
    anthropic_api_key = st.text_input(
        "API key de Anthropic",
        value=config.get("anthropic_api_key", ""),
        type="password",
    )
    google_api_key = st.text_input(
        "API key de Google",
        value=config.get("google_api_key", ""),
        type="password",
    )
    ollama_url = st.text_input(
        "URL de Ollama",
        value=config.get("ollama_url", "http://localhost:11434"),
        help="Ejemplo: http://localhost:11434",
    )

    saved = st.form_submit_button("Guardar configuración", type="primary")

if saved:
    st.session_state["tutor_config"] = {
        "openai_api_key": openai_api_key.strip(),
        "anthropic_api_key": anthropic_api_key.strip(),
        "google_api_key": google_api_key.strip(),
        "ollama_url": ollama_url.strip() or "http://localhost:11434",
    }
    st.success("Configuración guardada en la sesión actual.")

st.info(
    "Para persistir claves fuera de la sesión, usa `.streamlit/secrets.toml` "
    "a partir del template `secrets.toml.example`."
)
