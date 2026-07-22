"""Aplicación principal del tutor RAG para Ingeniería Eléctrica."""

from __future__ import annotations

import streamlit as st
from httpx import HTTPError
from openai import OpenAIError
from streamlit.errors import StreamlitSecretNotFoundError

try:
    from anthropic import APIError as AnthropicAPIError
except ImportError:  # pragma: no cover - dependiente del entorno
    AnthropicAPIError = RuntimeError

try:
    from google.api_core.exceptions import GoogleAPIError
except ImportError:  # pragma: no cover - dependiente del entorno
    GoogleAPIError = RuntimeError

from core.llm_factory import PROVIDER_MODELS, get_llm
from core.rag_pipeline import ask_tutor, create_rag_chain

ASIGNATURAS = {
    "Circuitos eléctricos": "circuitos",
    "Electrónica": "electronica",
    "Máquinas eléctricas": "maquinas_electricas",
}

CONFIG_KEYS = {
    "OpenAI": "openai_api_key",
    "Anthropic": "anthropic_api_key",
    "Google": "google_api_key",
}


def _inicializar_estado() -> None:
    """Inicializa el estado global de la app."""
    def _secret(nombre: str, default: str) -> str:
        """Lee una clave de `st.secrets` sin fallar si no existe archivo de secretos."""
        try:
            return st.secrets.get(nombre, default)
        except StreamlitSecretNotFoundError:
            return default

    st.session_state.setdefault(
        "tutor_config",
        {
            "openai_api_key": _secret("OPENAI_API_KEY", ""),
            "anthropic_api_key": _secret("ANTHROPIC_API_KEY", ""),
            "google_api_key": _secret("GOOGLE_API_KEY", ""),
            "ollama_url": _secret("OLLAMA_URL", "http://localhost:11434"),
        },
    )
    st.session_state.setdefault(
        "tutor_messages",
        [
            {
                "role": "assistant",
                "content": (
                    "Hola, soy tu tutor de Ingeniería Eléctrica. "
                    "Haz una pregunta sobre la asignatura seleccionada."
                ),
            }
        ],
    )
    st.session_state.setdefault("tutor_chain", None)
    st.session_state.setdefault("tutor_chain_config", None)


def _mensaje_error(exc: Exception, provider: str) -> str:
    """Convierte excepciones técnicas en mensajes claros para la interfaz."""
    raw = str(exc)
    text = raw.lower()

    if "no hay documentos indexados" in text:
        return raw
    if any(token in text for token in ("401", "unauthorized", "authentication", "api key")):
        return "La API key es inválida o no tiene permisos para el modelo seleccionado."
    if provider == "Ollama" and any(token in text for token in ("connection", "refused", "connect")):
        return (
            "No fue posible conectarse con Ollama. "
            "Verifica que esté activo y que la URL sea correcta."
        )
    return f"Ocurrió un error al generar la respuesta: {raw}"


_inicializar_estado()

st.set_page_config(page_title="Tutor RAG de Ingeniería Eléctrica", page_icon=":material/school:")
st.title("Tutor RAG de Ingeniería Eléctrica")
st.caption("Responde con base en el contenido indexado por asignatura")

with st.sidebar:
    st.subheader("Configuración del tutor")
    asignatura_label = st.selectbox("Asignatura", list(ASIGNATURAS.keys()))
    asignatura = ASIGNATURAS[asignatura_label]

    provider = st.selectbox("Proveedor LLM", list(PROVIDER_MODELS.keys()))
    model = st.selectbox("Modelo", PROVIDER_MODELS[provider])

    config = st.session_state["tutor_config"]
    api_key = ""
    ollama_url = config.get("ollama_url", "http://localhost:11434")

    if provider == "Ollama":
        st.info("Para Ollama no se requiere API key.")
        ollama_url = st.text_input(
            "URL de Ollama",
            value=ollama_url,
            key="tutor_ollama_url_runtime",
            help="Ejemplo: http://localhost:11434",
        )
        config["ollama_url"] = ollama_url
    else:
        key_name = CONFIG_KEYS[provider]
        api_key = st.text_input(
            f"API key de {provider}",
            type="password",
            value=config.get(key_name, ""),
            key=f"tutor_api_key_{provider.lower()}",
        )
        if api_key:
            config[key_name] = api_key

for msg in st.session_state["tutor_messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Escribe tu pregunta del material cargado"):
    if provider != "Ollama" and not api_key:
        st.info(f"Agrega tu API key de {provider} para continuar.")
        st.stop()

    st.session_state["tutor_messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        llm = get_llm(provider=provider, model=model, api_key=api_key, ollama_url=ollama_url)
        chain_config = (asignatura, provider, model, api_key, ollama_url)
        if st.session_state["tutor_chain"] is None or st.session_state["tutor_chain_config"] != chain_config:
            st.session_state["tutor_chain"] = create_rag_chain(
                asignatura=asignatura,
                llm=llm,
                openai_api_key=st.session_state["tutor_config"].get("openai_api_key") or None,
            )
            st.session_state["tutor_chain_config"] = chain_config

        answer, sources = ask_tutor(st.session_state["tutor_chain"], prompt)
        if sources:
            answer = f"{answer}\n\n**Fuentes:** {', '.join(sources)}"
        else:
            answer = f"{answer}\n\n**Fuentes:** No disponibles."

    except (
        ValueError,
        RuntimeError,
        OSError,
        ConnectionError,
        OpenAIError,
        AnthropicAPIError,
        GoogleAPIError,
        HTTPError,
    ) as exc:
        answer = _mensaje_error(exc, provider)

    st.session_state["tutor_messages"].append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
