"""Page for uploading PDFs by course and indexing them in ChromaDB."""

from __future__ import annotations

import streamlit as st
from openai import OpenAIError

from core.vector_store import ingest_documents, list_indexed_documents
from frontend.i18n import LANGUAGE_OPTIONS, get_translations

# --- i18n ---
st.session_state.setdefault("lang", "es")
t = get_translations(st.session_state["lang"])

ASIGNATURAS = {
    "es": {
        "Circuitos eléctricos": "circuitos",
        "Electrónica": "electronica",
        "Máquinas eléctricas": "maquinas_electricas",
    },
    "en": {
        "Electric Circuits": "circuitos",
        "Electronics": "electronica",
        "Electric Machines": "maquinas_electricas",
    },
}

st.set_page_config(page_title=t["upload_page_title"], page_icon=":material/upload_file:")

# --- Language selector in sidebar ---
with st.sidebar:
    lang_label = st.selectbox(
        "🌐 Language / Idioma",
        list(LANGUAGE_OPTIONS.keys()),
        index=0 if st.session_state["lang"] == "es" else 1,
        key="lang_selector_upload",
    )
    st.session_state["lang"] = LANGUAGE_OPTIONS[lang_label]
    t = get_translations(st.session_state["lang"])

st.title(t["upload_page_title"])
st.caption(t["upload_page_caption"])

st.session_state.setdefault(
    "tutor_config",
    {
        "openai_api_key": "",
        "anthropic_api_key": "",
        "google_api_key": "",
        "ollama_url": "http://localhost:11434",
    },
)
openai_api_key = st.session_state["tutor_config"].get("openai_api_key") or None

course_map = ASIGNATURAS[st.session_state["lang"]]
asignatura_label = st.selectbox(t["label_target_course"], list(course_map.keys()))
asignatura = course_map[asignatura_label]

uploaded_files = st.file_uploader(
    t["label_select_pdfs"],
    type=["pdf"],
    accept_multiple_files=True,
)

if st.button(t["btn_index"], type="primary"):
    if not uploaded_files:
        st.warning(t["warn_no_files"])
    else:
        progress = st.progress(0)
        total_chunks = 0
        total_files = len(uploaded_files)

        try:
            with st.status(t["status_indexing"], expanded=True) as status:
                for index, file_obj in enumerate(uploaded_files, start=1):
                    status.write(f"{t['status_processing']} {file_obj.name}")
                    chunks = ingest_documents(
                        pdf_files=[file_obj],
                        asignatura=asignatura,
                        openai_api_key=openai_api_key,
                    )
                    total_chunks += chunks
                    progress.progress(int(index * 100 / total_files))
                status.update(label=t["status_done"], state="complete")

            st.success(t["success_indexed"].format(chunks=total_chunks, course=asignatura_label))
        except (ValueError, RuntimeError, OSError, ConnectionError, OpenAIError) as exc:
            st.error(str(exc))

st.subheader(t["subheader_indexed_docs"])
try:
    indexed_docs = list_indexed_documents(asignatura=asignatura, openai_api_key=openai_api_key)
    if indexed_docs:
        for file_name in indexed_docs:
            st.write(f"- {file_name}")
    else:
        st.info(t["info_no_docs"])
except RuntimeError as exc:
    st.error(str(exc))
