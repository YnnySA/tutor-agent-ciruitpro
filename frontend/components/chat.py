"""Componentes de chat: renderizado del historial y manejo de input del estudiante."""

from __future__ import annotations

import streamlit as st
from httpx import HTTPError
from openai import OpenAIError

try:
    from anthropic import APIError as AnthropicAPIError
except ImportError:
    AnthropicAPIError = RuntimeError  # type: ignore[assignment,misc]

try:
    from google.api_core.exceptions import GoogleAPIError
except ImportError:
    GoogleAPIError = RuntimeError  # type: ignore[assignment,misc]

from backend.llm_factory import get_llm
from backend.rag_pipeline import ask_tutor, create_rag_chain


def _mensaje_error(exc: Exception, provider: str) -> str:
    """Convierte excepciones técnicas en mensajes claros para el estudiante."""
    raw = str(exc)
    text = raw.lower()
    if "no hay documentos indexados" in text:
        return raw
    if any(t in text for t in ("401", "unauthorized", "authentication", "api key")):
        return "La API key es inválida o no tiene permisos para el modelo seleccionado."
    if provider == "Ollama" and any(t in text for t in ("connection", "refused", "connect")):
        return (
            "No fue posible conectarse con Ollama. "
            "Verifica que esté activo y que la URL sea correcta."
        )
    return f"Ocurrió un error al generar la respuesta: {raw}"


def render_chat() -> None:
    """Renderiza el historial completo de mensajes desde session_state."""
    for msg in st.session_state["tutor_messages"]:
        st.chat_message(msg["role"]).write(msg["content"])


def handle_input(config: dict) -> None:
    """
    Captura el prompt del estudiante, consulta el backend RAG
    y guarda la respuesta en session_state.
    """
    provider = config["provider"]
    model = config["model"]
    asignatura = config["asignatura"]
    api_key = config["api_key"]
    ollama_url = config["ollama_url"]

    if prompt := st.chat_input("Escribe tu pregunta sobre el material de la asignatura"):
        if provider != "Ollama" and not api_key:
            st.info(f"Agrega tu API key de {provider} en el panel lateral para continuar.")
            st.stop()

        st.session_state["tutor_messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        try:
            llm = get_llm(
                provider=provider, model=model,
                api_key=api_key, ollama_url=ollama_url,
            )
            chain_config = (asignatura, provider, model, api_key, ollama_url)
            if (
                st.session_state["tutor_chain"] is None
                or st.session_state["tutor_chain_config"] != chain_config
            ):
                openai_key = st.session_state["tutor_config"].get("OPENAI_API_KEY") or None
                st.session_state["tutor_chain"] = create_rag_chain(
                    asignatura=asignatura,
                    llm=llm,
                    openai_api_key=openai_key,
                )
                st.session_state["tutor_chain_config"] = chain_config

            answer, sources = ask_tutor(st.session_state["tutor_chain"], prompt)
            fuentes_txt = ", ".join(sources) if sources else "No disponibles"
            answer = f"{answer}\n\n**Fuentes:** {fuentes_txt}"

        except (
            ValueError, RuntimeError, OSError, ConnectionError,
            OpenAIError, AnthropicAPIError, GoogleAPIError, HTTPError,
        ) as exc:
            answer = _mensaje_error(exc, provider)

        st.session_state["tutor_messages"].append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
