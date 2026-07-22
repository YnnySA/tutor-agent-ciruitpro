"""Componente visual para mostrar las fuentes RAG al estudiante."""

from __future__ import annotations

import streamlit as st


def render_sources(sources: list[str]) -> None:
    """Muestra las fuentes del RAG como badges compactos."""
    if not sources:
        return
    with st.expander("📚 Fuentes consultadas", expanded=False):
        for src in sources:
            st.markdown(f"- `{src}`")
