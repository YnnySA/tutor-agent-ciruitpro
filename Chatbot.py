"""Entry point del Tutor RAG — orquesta UI sin lógica de negocio."""

from __future__ import annotations

import streamlit as st

from frontend.state import inicializar_estado
from frontend.sidebar import render_sidebar
from frontend.components.chat import render_chat, handle_input

st.set_page_config(
    page_title="Tutor RAG · Ingeniería Eléctrica",
    page_icon="⚡",
    layout="centered",
)

st.title("Tutor RAG de Ingeniería Eléctrica")
st.caption("Consulta el material de tu asignatura con inteligencia artificial")

inicializar_estado()
config = render_sidebar()      # retorna: asignatura, provider, model, api_key, ollama_url
render_chat()                  # renderiza historial desde session_state
handle_input(config)           # captura prompt → consulta backend → guarda respuesta
