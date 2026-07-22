"""Pipeline RAG conversacional para el tutor de Ingeniería Eléctrica."""

from __future__ import annotations

import yaml
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate

try:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
except ModuleNotFoundError:
    from langchain_classic.chains import ConversationalRetrievalChain
    from langchain_classic.memory import ConversationBufferMemory

from backend.vector_store import get_retriever

ROOT = Path(__file__).resolve().parent.parent


def _get_temario(asignatura: str) -> str:
    """Lee el temario de la asignatura desde config/asignaturas.yaml."""
    config_path = ROOT / "config" / "asignaturas.yaml"
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["asignaturas"].get(asignatura, {}).get(
        "temario", "temario no especificado"
    )


def _build_prompt(asignatura: str) -> PromptTemplate:
    """Construye el prompt del tutor con alcance controlado por asignatura."""
    temario = _get_temario(asignatura)
    template = """
Eres un tutor experto en Ingeniería Eléctrica.
Responde siempre en español con explicaciones pedagógicas y paso a paso cuando sea necesario.

Asignatura activa: {asignatura}
Temario permitido: {temario}

Reglas de alcance:
1. Usa únicamente el contexto recuperado del material cargado.
2. Si la pregunta está fuera del contenido disponible o del temario, indícalo claramente.
3. Cuando proceda, incluye ejemplos y razonamiento guiado.

Contexto recuperado:
{context}

Historial de conversación:
{chat_history}

Pregunta del estudiante:
{question}

Respuesta del tutor:
"""
    return PromptTemplate(
        template=template,
        input_variables=["context", "chat_history", "question"],
        partial_variables={"asignatura": asignatura, "temario": temario},
    )


def create_rag_chain(
    asignatura: str,
    llm: BaseChatModel,
    openai_api_key: str | None = None,
) -> ConversationalRetrievalChain:
    """Crea una cadena RAG conversacional con memoria y documentos fuente."""
    retriever = get_retriever(
        asignatura=asignatura, openai_api_key=openai_api_key
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        return_messages=False,
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": _build_prompt(asignatura)},
    )


def ask_tutor(
    chain: ConversationalRetrievalChain, question: str
) -> tuple[str, list[str]]:
    """Ejecuta la consulta al tutor y devuelve respuesta más fuentes."""
    result = chain.invoke({"question": question})
    answer = (result.get("answer") or "").strip()
    sources: list[str] = []
    for doc in result.get("source_documents") or []:
        src = Path((doc.metadata or {}).get("source", "")).name
        if src and src not in sources:
            sources.append(src)
    return answer, sources
