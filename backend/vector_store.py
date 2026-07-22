"""Gestión de ChromaDB: indexación desde directorio y recuperación por asignatura."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import yaml
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.retrievers import BaseRetriever
from langchain_openai import OpenAIEmbeddings

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ModuleNotFoundError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = ROOT / "chroma_db"
CONFIG_ASIG = ROOT / "config" / "asignaturas.yaml"
CONFIG_SETTINGS = ROOT / "config" / "settings.yaml"


def _load_settings() -> dict:
    with open(CONFIG_SETTINGS, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_asig_config() -> dict:
    with open(CONFIG_ASIG, encoding="utf-8") as f:
        return yaml.safe_load(f)["asignaturas"]


def _collection_name(asignatura: str) -> str:
    cfg = _load_asig_config()
    if asignatura not in cfg:
        raise ValueError(f"Asignatura inválida: '{asignatura}'. Opciones: {list(cfg.keys())}")
    return cfg[asignatura]["collection_id"]


def _get_embeddings(openai_api_key: str | None = None) -> Any:
    """Embeddings con OpenAI y fallback a HuggingFace."""
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    settings = _load_settings()
    if api_key:
        return OpenAIEmbeddings(
            model=settings["rag"]["embeddings_model"], api_key=api_key
        )
    try:
        return HuggingFaceEmbeddings(
            model_name=settings["rag"]["embeddings_fallback"]
        )
    except ImportError as exc:
        raise RuntimeError(
            "No fue posible inicializar embeddings locales. "
            "Instala sentence-transformers o configura OPENAI_API_KEY."
        ) from exc


def _get_vector_store(asignatura: str, openai_api_key: str | None = None) -> Chroma:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=_collection_name(asignatura),
        persist_directory=str(CHROMA_DIR),
        embedding_function=_get_embeddings(openai_api_key=openai_api_key),
    )


def _drop_collection(asignatura: str) -> None:
    """Elimina la colección de ChromaDB para reindexar desde cero."""
    vs = _get_vector_store(asignatura)
    vs._client.delete_collection(_collection_name(asignatura))


# ------------------------------------------------------------------ #
#  PRINCIPAL: indexación desde directorio local (documentación curada) #
# ------------------------------------------------------------------ #

def ingest_from_directory(
    asignatura: str,
    openai_api_key: str | None = None,
    force_reindex: bool = False,
) -> int:
    """
    Lee todos los PDFs desde config/asignaturas.yaml[asignatura][pdf_dir]
    y los indexa en ChromaDB.
    - force_reindex=True: borra la colección y reconstruye desde cero.
    - Retorna el número de chunks indexados.
    """
    asig_cfg = _load_asig_config()
    if asignatura not in asig_cfg:
        raise ValueError(f"Asignatura no definida: '{asignatura}'")

    settings = _load_settings()
    pdf_dir = ROOT / asig_cfg[asignatura]["pdf_dir"]
    pdfs = list(pdf_dir.glob("*.pdf"))

    if not pdfs:
        raise FileNotFoundError(
            f"No hay PDFs en '{pdf_dir}'. "
            "Coloca el material del cliente ahí antes de indexar."
        )

    if force_reindex:
        _drop_collection(asignatura)

    documentos = []
    for pdf_path in pdfs:
        loader = PyPDFLoader(str(pdf_path))
        for doc in loader.load():
            doc.metadata["source"] = pdf_path.name
            doc.metadata["asignatura"] = asignatura
            documentos.append(doc)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings["rag"]["chunk_size"],
        chunk_overlap=settings["rag"]["chunk_overlap"],
    )
    chunks = splitter.split_documents(documentos)
    vs = _get_vector_store(asignatura, openai_api_key)
    vs.add_documents(chunks)
    vs.persist()
    return len(chunks)


# ------------------------------------------------------------------ #
#  LEGACY: ingesta dinámica por file_obj (mantiene compatibilidad)    #
# ------------------------------------------------------------------ #

def ingest_documents(
    pdf_files: Iterable[Any],
    asignatura: str,
    openai_api_key: str | None = None,
) -> int:
    """Ingresa PDFs recibidos como file objects (compatibilidad con uploads)."""
    settings = _load_settings()
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

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings["rag"]["chunk_size"],
        chunk_overlap=settings["rag"]["chunk_overlap"],
    )
    chunks = splitter.split_documents(documentos)
    vs = _get_vector_store(asignatura=asignatura, openai_api_key=openai_api_key)
    vs.add_documents(chunks)
    vs.persist()
    return len(chunks)


def get_retriever(
    asignatura: str,
    k: int | None = None,
    openai_api_key: str | None = None,
) -> BaseRetriever:
    """Retorna el retriever para la asignatura; falla claro si no hay documentos."""
    settings = _load_settings()
    k = k or settings["rag"]["retrieval_k"]
    vs = _get_vector_store(asignatura=asignatura, openai_api_key=openai_api_key)
    if vs._collection.count() == 0:
        raise ValueError(
            f"No hay documentos indexados para '{asignatura}'. "
            f"Ejecuta: python scripts/index_docs.py --asignatura {asignatura}"
        )
    return vs.as_retriever(search_kwargs={"k": k})


def list_indexed_documents(
    asignatura: str, openai_api_key: str | None = None
) -> list[str]:
    """Lista nombres de PDFs indexados en la asignatura seleccionada."""
    vs = _get_vector_store(asignatura=asignatura, openai_api_key=openai_api_key)
    metadatas = vs.get(include=["metadatas"]).get("metadatas") or []
    fuentes = {
        (m or {}).get("source", "")
        for m in metadatas
        if (m or {}).get("source")
    }
    return sorted(fuentes)
