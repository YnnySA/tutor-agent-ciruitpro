"""Page for configuring LLM credentials and Ollama URL."""

from __future__ import annotations

import streamlit as st

from frontend.i18n import LANGUAGE_OPTIONS, get_translations

# --- i18n ---
st.session_state.setdefault("lang", "es")
t = get_translations(st.session_state["lang"])

st.set_page_config(page_title=t["settings_page_title"], page_icon=":material/settings:")

# --- Language selector in sidebar ---
with st.sidebar:
    lang_label = st.selectbox(
        "🌐 Language / Idioma",
        list(LANGUAGE_OPTIONS.keys()),
        index=0 if st.session_state["lang"] == "es" else 1,
        key="lang_selector_settings",
    )
    st.session_state["lang"] = LANGUAGE_OPTIONS[lang_label]
    t = get_translations(st.session_state["lang"])

st.title(t["settings_page_title"])
st.caption(t["settings_page_caption"])

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

with st.form("settings_llm"):
    openai_api_key = st.text_input(
        t["label_openai_key"],
        value=config.get("openai_api_key", ""),
        type="password",
    )
    anthropic_api_key = st.text_input(
        t["label_anthropic_key"],
        value=config.get("anthropic_api_key", ""),
        type="password",
    )
    google_api_key = st.text_input(
        t["label_google_key"],
        value=config.get("google_api_key", ""),
        type="password",
    )
    ollama_url = st.text_input(
        t["label_ollama_url"],
        value=config.get("ollama_url", "http://localhost:11434"),
        help=t["ollama_help"],
    )

    saved = st.form_submit_button(t["btn_save_settings"], type="primary")

if saved:
    st.session_state["tutor_config"] = {
        "openai_api_key": openai_api_key.strip(),
        "anthropic_api_key": anthropic_api_key.strip(),
        "google_api_key": google_api_key.strip(),
        "ollama_url": ollama_url.strip() or "http://localhost:11434",
    }
    st.success(t["success_settings_saved"])

st.info(t["info_secrets_hint"])
