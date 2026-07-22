"""Página para cargar PDFs por asignatura e indexarlos en ChromaDB."""

from __future__ import annotations

import streamlit as st
from openai import OpenAIError

from core.vector_store import ingest_documents, list_indexed_documents

ASIGNATURAS = {
    "Circuitos eléctricos": "circuitos",
    "Electrónica": "electronica",
    "Máquinas eléctricas": "maquinas_electricas",
}

st.set_page_config(page_title="Cargar contenido", page_icon=":material/upload_file:")
st.title("Cargar contenido para el tutor")
st.caption("Sube PDFs y asócialos a una asignatura para indexarlos en ChromaDB")

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

asignatura_label = st.selectbox("Asignatura destino", list(ASIGNATURAS.keys()))
asignatura = ASIGNATURAS[asignatura_label]

uploaded_files = st.file_uploader(
    "Selecciona uno o varios PDFs",
    type=["pdf"],
    accept_multiple_files=True,
)

if st.button("Indexar en ChromaDB", type="primary"):
    if not uploaded_files:
        st.warning("Primero debes cargar al menos un archivo PDF.")
    else:
        progress = st.progress(0)
        total_chunks = 0
        total_files = len(uploaded_files)

        try:
            with st.status("Indexando documentos...", expanded=True) as status:
                for index, file_obj in enumerate(uploaded_files, start=1):
                    status.write(f"Procesando: {file_obj.name}")
                    chunks = ingest_documents(
                        pdf_files=[file_obj],
                        asignatura=asignatura,
                        openai_api_key=openai_api_key,
                    )
                    total_chunks += chunks
                    progress.progress(int(index * 100 / total_files))
                status.update(label="Indexación completada", state="complete")

            st.success(f"Se indexaron {total_chunks} chunks en la asignatura '{asignatura_label}'.")
        except (ValueError, RuntimeError, OSError, ConnectionError, OpenAIError) as exc:
            st.error(str(exc))

st.subheader("Documentos indexados")
try:
    indexed_docs = list_indexed_documents(asignatura=asignatura, openai_api_key=openai_api_key)
    if indexed_docs:
        for file_name in indexed_docs:
            st.write(f"- {file_name}")
    else:
        st.info("Aún no hay documentos indexados para esta asignatura.")
except RuntimeError as exc:
    st.error(str(exc))
