"""Orquestador de indexación — sin dependencias de Streamlit."""

from __future__ import annotations

import yaml
from pathlib import Path

from backend.vector_store import ingest_from_directory, _get_vector_store

ROOT = Path(__file__).resolve().parent.parent


def load_asignaturas() -> dict:
    """Carga el mapa de asignaturas desde config/asignaturas.yaml."""
    config_path = ROOT / "config" / "asignaturas.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)["asignaturas"]


def index_asignatura(asig_id: str, force: bool = False) -> int:
    """Indexa una asignatura específica. Retorna número de chunks."""
    return ingest_from_directory(asig_id, force_reindex=force)


def index_all(force: bool = False) -> dict[str, int | str]:
    """Indexa todas las asignaturas definidas en config/asignaturas.yaml."""
    resultados: dict[str, int | str] = {}
    for asig_id in load_asignaturas():
        try:
            resultados[asig_id] = index_asignatura(asig_id, force)
        except FileNotFoundError:
            resultados[asig_id] = "sin PDFs aún"
    return resultados


def chroma_status() -> dict[str, int]:
    """Retorna número de chunks indexados por asignatura en ChromaDB."""
    status: dict[str, int] = {}
    for asig_id in load_asignaturas():
        try:
            vs = _get_vector_store(asig_id)
            status[asig_id] = vs._collection.count()
        except Exception:
            status[asig_id] = 0
    return status
