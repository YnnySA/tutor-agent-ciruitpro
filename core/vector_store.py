"""Gestión de ChromaDB para indexación y recuperación por asignatura."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.retrievers import BaseRetriever

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ModuleNotFoundError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
ASIGNATURA_COLLECTION = {
    "circuitos": "circuitos",
    "electronica": "electronica",
    "maquinas_electricas": "maquinas",
}

# Modelo Ollama por defecto — cambiar a qwen3-embedding:4b para mayor calidad
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:0.6b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def _collection_name(asignatura: str) -> str:
    if asignatura not in ASIGNATURA_COLLECTION:
        disponibles = ", ".join(ASIGNATURA_COLLECTION.keys())
        raise ValueError(f"Asignatura inválida: {asignatura}. Opciones: {disponibles}")
    return ASIGNATURA_COLLECTION[asignatura]


def _get_embeddings(openai_api_key: str | None = None) -> Any:
    """
    Estrategia de embeddings (en orden de prioridad):
    1. OpenAI text-embedding-3-small  → si hay OPENAI_API_KEY
    2. Ollama qwen3-embedding:0.6b    → modelo local, sin API key (default)
    Para escalar: cambiar OLLAMA_EMBEDDING_MODEL=qwen3-embedding:4b y reindexar.
    """
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    # --- Opción 1: OpenAI ---
    if api_key:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)

    # --- Opción 2: Ollama local (qwen3-embedding:0.6b) ---
    try:
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL, base_url=OLLAMA_URL)
    except Exception as exc:
        raise RuntimeError(
            "No fue posible conectar con Ollama para los embeddings.\n"
            "Asegúrate de que Ollama esté activo y ejecuta:\n"
            f"  ollama pull {OLLAMA_EMBEDDING_MODEL}\n"
            "O configura OPENAI_API_KEY como alternativa."
        ) from exc


def _get_vector_store(asignatura: str, openai_api_key: str | None = None) -> Chroma:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=_collection_name(asignatura),
        persist_directory=str(CHROMA_DIR),
        embedding_function=_get_embeddings(openai_api_key=openai_api_key),
    )


def ingest_documents(
    pdf_files: Iterable[Any],
    asignatura: str,
    openai_api_key: str | None = None,
) -> int:
    """Ingresa PDFs en Chroma y devuelve la cantidad de chunks indexados."""
    documentos = []
    for file_obj in pdf_files:
        file_name = getattr(file_obj, "name", "documento.pdf")
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        payload = file_obj.read()
        if not payload:
            continue
        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(payload)
                temp_path = tmp.name
            loader = PyPDFLoader(temp_path)
            for doc in loader.load():
                doc.metadata["source"] = file_name
                documentos.append(doc)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    if not documentos:
        raise ValueError("No se detectó contenido válido en los PDFs cargados.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documentos)
    if not chunks:
        raise ValueError("No se pudieron generar chunks del contenido cargado.")

    vector_store = _get_vector_store(asignatura=asignatura, openai_api_key=openai_api_key)
    vector_store.add_documents(chunks)
    vector_store.persist()
    return len(chunks)


def get_retriever(
    asignatura: str,
    k: int = 4,
    openai_api_key: str | None = None,
) -> BaseRetriever:
    """Retorna el retriever; error claro si no hay documentos indexados."""
    vector_store = _get_vector_store(asignatura=asignatura, openai_api_key=openai_api_key)
    if vector_store._collection.count() == 0:
        raise ValueError(
            "No hay documentos indexados para esta asignatura. "
            "Carga PDFs en la página 'Cargar contenido'."
        )
    return vector_store.as_retriever(search_kwargs={"k": k})


def list_indexed_documents(asignatura: str, openai_api_key: str | None = None) -> list[str]:
    """Lista nombres de PDFs indexados en la asignatura seleccionada."""
    vector_store = _get_vector_store(asignatura=asignatura, openai_api_key=openai_api_key)
    metadatas = vector_store.get(include=["metadatas"]).get("metadatas") or []
    fuentes = {
        (m or {}).get("source", "")
        for m in metadatas
        if (m or {}).get("source")
    }
    return sorted(fuentes)
