"""Pruebas básicas del tutor RAG."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core import llm_factory, vector_store


@patch("langchain_openai.ChatOpenAI")
def test_get_llm_openai(ChatOpenAIMock):
    """Verifica que la fábrica cree un modelo OpenAI con parámetros correctos."""
    llm_instance = MagicMock()
    ChatOpenAIMock.return_value = llm_instance

    llm = llm_factory.get_llm(
        provider="OpenAI",
        model="gpt-4o-mini",
        api_key="sk-test",
    )

    ChatOpenAIMock.assert_called_once_with(
        model="gpt-4o-mini",
        api_key="sk-test",
        temperature=0.2,
    )
    assert llm is llm_instance


@patch("core.vector_store._get_vector_store")
def test_get_retriever_sin_documentos(get_vector_store_mock):
    """Valida que se informe error cuando no hay contenido indexado."""
    collection = MagicMock()
    collection.count.return_value = 0

    store = MagicMock()
    store._collection = collection
    get_vector_store_mock.return_value = store

    with pytest.raises(ValueError, match="No hay documentos indexados"):
        vector_store.get_retriever(asignatura="circuitos")
