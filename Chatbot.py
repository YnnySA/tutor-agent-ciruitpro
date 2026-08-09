"""Aplicación principal del tutor RAG para Ingeniería Eléctrica."""

from __future__ import annotations

import streamlit as st
from httpx import HTTPError
from openai import OpenAIError
from streamlit.errors import StreamlitSecretNotFoundError

try:
    from anthropic import APIError as AnthropicAPIError
except ImportError:  # pragma: no cover
    AnthropicAPIError = RuntimeError

try:
    from google.api_core.exceptions import GoogleAPIError
except ImportError:  # pragma: no cover
    GoogleAPIError = RuntimeError

from core.llm_factory import PROVIDER_MODELS, get_llm
from core.rag_pipeline import ask_tutor, create_rag_chain
from frontend.i18n import LANGUAGE_OPTIONS, get_translations

ASIGNATURAS = {
    "Circuitos eléctricos": "circuitos",
    "Electrónica": "electronica",
    "Máquinas eléctricas": "maquinas_electricas",
}

ASIGNATURAS_EN = {
    "Electric Circuits": "circuitos",
    "Electronics": "electronica",
    "Electric Machines": "maquinas_electricas",
}

CONFIG_KEYS = {
    "OpenAI": "openai_api_key",
    "Anthropic": "anthropic_api_key",
    "Google": "google_api_key",
}


def _inicializar_estado() -> None:
    """Inicializa el estado global de la app."""
    def _secret(nombre: str, default: str) -> str:
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
    st.session_state.setdefault("tutor_chain", None)
    st.session_state.setdefault("tutor_chain_config", None)
    st.session_state.setdefault("lang", "es")


def _init_messages(t: dict) -> None:
    """Inicializa o reinicia los mensajes si cambia el idioma."""
    welcome = t["welcome_message"]
    messages = st.session_state.get("tutor_messages", [])
    if not messages or messages[0]["content"] != welcome:
        st.session_state["tutor_messages"] = [
            {"role": "assistant", "content": welcome}
        ]


def _mensaje_error(exc: Exception, provider: str, t: dict) -> str:
    """Convierte excepciones técnicas en mensajes claros para la interfaz."""
    raw = str(exc)
    text = raw.lower()

    if "no hay documentos indexados" in text:
        return raw
    if any(token in text for token in ("401", "unauthorized", "authentication", "api key")):
        return t["error_invalid_key"]
    if provider == "Ollama" and any(token in text for token in ("connection", "refused", "connect")):
        return t["error_ollama_connection"]
    return t["error_generic"].format(raw=raw)


_inicializar_estado()

# --- Language selector (top of sidebar, affects everything) ---
with st.sidebar:
    lang_label = st.selectbox(
        "🌐 Language / Idioma",
        list(LANGUAGE_OPTIONS.keys()),
        index=0 if st.session_state["lang"] == "es" else 1,
        key="lang_selector",
    )
    st.session_state["lang"] = LANGUAGE_OPTIONS[lang_label]

t = get_translations(st.session_state["lang"])
_init_messages(t)

# --- Page config & header ---
st.set_page_config(page_title=t["page_title"], page_icon=":material/school:")
st.title(t["app_title"])
st.caption(t["app_caption"])

# --- Sidebar config ---
course_map = ASIGNATURAS_EN if st.session_state["lang"] == "en" else ASIGNATURAS

with st.sidebar:
    st.subheader(t["sidebar_title"])
    asignatura_label = st.selectbox(t["label_course"], list(course_map.keys()))
    asignatura = course_map[asignatura_label]

    provider = st.selectbox(t["label_provider"], list(PROVIDER_MODELS.keys()))
    model = st.selectbox(t["label_model"], PROVIDER_MODELS[provider])

    config = st.session_state["tutor_config"]
    api_key = ""
    ollama_url = config.get("ollama_url", "http://localhost:11434")

    if provider == "Ollama":
        st.info(t["ollama_info"])
        ollama_url = st.text_input(
            t["label_ollama_url"],
            value=ollama_url,
            key="tutor_ollama_url_runtime",
            help=t["ollama_help"],
        )
        config["ollama_url"] = ollama_url
    else:
        key_name = CONFIG_KEYS[provider]
        api_key = st.text_input(
            f"{t['label_api_key']} {provider}",
            type="password",
            value=config.get(key_name, ""),
            key=f"tutor_api_key_{provider.lower()}",
        )
        if api_key:
            config[key_name] = api_key

# --- Chat messages ---
for msg in st.session_state["tutor_messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(t["chat_placeholder"]):
    if provider != "Ollama" and not api_key:
        st.info(t["error_no_api_key"].format(provider=provider))
        st.stop()

    st.session_state["tutor_messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        llm = get_llm(provider=provider, model=model, api_key=api_key, ollama_url=ollama_url)
        chain_config = (asignatura, provider, model, api_key, ollama_url)
        if (
            st.session_state["tutor_chain"] is None
            or st.session_state["tutor_chain_config"] != chain_config
        ):
            st.session_state["tutor_chain"] = create_rag_chain(
                asignatura=asignatura,
                llm=llm,
                openai_api_key=st.session_state["tutor_config"].get("openai_api_key") or None,
            )
            st.session_state["tutor_chain_config"] = chain_config

        answer, sources = ask_tutor(st.session_state["tutor_chain"], prompt)
        src_label = t["sources_label"]
        src_none = t["sources_unavailable"]
        if sources:
            answer = f"{answer}\n\n**{src_label}:** {', '.join(sources)}"
        else:
            answer = f"{answer}\n\n**{src_label}:** {src_none}"

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
        answer = _mensaje_error(exc, provider, t)

    st.session_state["tutor_messages"].append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
