"""Gestión de ChromaDB para indexación y recuperación por asignatura."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.retrievers import BaseRetriever
from langchain_openai import OpenAIEmbeddings

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ModuleNotFoundError:  # pragma: no cover - compatibilidad LangChain 1.x
    from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
ASIGNATURA_COLLECTION = {
    "circuitos": "circuitos",
    "electronica": "electronica",
    "maquinas_electricas": "maquinas",
}


def _collection_name(asignatura: str) -> str:
    """Mapea el identificador de asignatura al nombre de colección de Chroma."""
    if asignatura not in ASIGNATURA_COLLECTION:
        disponibles = ", ".join(ASIGNATURA_COLLECTION.keys())
        raise ValueError(f"Asignatura inválida: {asignatura}. Opciones: {disponibles}")
    return ASIGNATURA_COLLECTION[asignatura]


def _get_embeddings(openai_api_key: str | None = None) -> Any:
    """Inicializa embeddings con OpenAI y fallback a HuggingFace."""
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
    try:
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    except ImportError as exc:
        raise RuntimeError(
            "No fue posible inicializar embeddings locales. "
            "Instala sentence-transformers o configura OPENAI_API_KEY."
        ) from exc


def _get_vector_store(asignatura: str, openai_api_key: str | None = None) -> Chroma:
    """Construye la instancia de vector store para una asignatura."""
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
            loaded_docs = loader.load()
            for doc in loaded_docs:
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
    """Retorna el retriever para la asignatura; falla si no hay documentos."""
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
        (metadata or {}).get("source", "")
        for metadata in metadatas
        if (metadata or {}).get("source")
    }
    return sorted(fuentes)
