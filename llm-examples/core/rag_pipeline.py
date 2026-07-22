"""Pipeline RAG conversacional para el tutor de Ingeniería Eléctrica."""

from __future__ import annotations

from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate

try:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
except ModuleNotFoundError:  # pragma: no cover - compatibilidad LangChain 1.x
    from langchain_classic.chains import ConversationalRetrievalChain
    from langchain_classic.memory import ConversationBufferMemory

from .vector_store import get_retriever

TEMARIO_ASIGNATURA = {
    "circuitos": "leyes de Kirchhoff, análisis nodal y de mallas, teoremas de redes y respuesta transitoria.",
    "electronica": "diodos, transistores, amplificadores, polarización, modelos de pequeña señal y electrónica analógica/digital básica.",
    "maquinas_electricas": "transformadores, máquinas DC/AC, circuitos equivalentes, ensayos, regulación y rendimiento.",
}


def _build_prompt(asignatura: str) -> PromptTemplate:
    """Construye el prompt del tutor con alcance controlado por asignatura."""
    temario = TEMARIO_ASIGNATURA.get(asignatura, "temario no especificado")
    template = """
Eres un tutor experto en Ingeniería Eléctrica.
Responde siempre en español con explicaciones pedagógicas y paso a paso cuando sea necesario.

Asignatura activa: {asignatura}
Temario permitido: {temario}

Reglas de alcance:
1. Usa únicamente el contexto recuperado del material cargado.
2. Si la pregunta está fuera del contenido disponible o del temario de la asignatura, indícalo claramente.
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
    retriever = get_retriever(asignatura=asignatura, k=4, openai_api_key=openai_api_key)
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


def ask_tutor(chain: ConversationalRetrievalChain, question: str) -> tuple[str, list[str]]:
    """Ejecuta la consulta al tutor y devuelve respuesta más fuentes."""
    result = chain.invoke({"question": question})
    answer = (result.get("answer") or "").strip()
    source_documents = result.get("source_documents") or []

    sources: list[str] = []
    for doc in source_documents:
        source = Path((doc.metadata or {}).get("source", "")).name
        if source and source not in sources:
            sources.append(source)

    return answer, sources
