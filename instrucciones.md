## CONTEXTO DEL PROYECTO BASE

Estoy trabajando en un fork local del repositorio `streamlit/llm-examples` 
(https://github.com/streamlit/llm-examples). La estructura actual del proyecto es:

llm-examples/
├── Chatbot.py ← Entry point actual (chatbot simple con OpenAI)
├── pages/
│ ├── 1_File_Q&A.py
│ ├── 2_Chat_with_search.py
│ ├── 3_Langchain_Quickstart.py
│ ├── 4_Langchain_PromptTemplate.py
│ └── 5_Chat_with_user_feedback.py
├── requirements.txt ← Tiene: streamlit, langchain, openai, anthropic
├── app_test.py
└── .devcontainer/


El `Chatbot.py` actual usa solo OpenAI con `st.session_state` para historial.
El `requirements.txt` actual incluye: streamlit>=1.28, langchain==0.0.350, 
openai>=1.2, anthropic>=0.3.0, langchain-community==0.0.3

---

## TAREA: Transformar en Agente Tutor RAG de Circuitos Eléctricos 

Necesito que **modifiques y extiendas** este proyecto existente para crear 
un agente tutor con arquitectura RAG. NO crear un proyecto desde cero, 
trabajar SOBRE los archivos existentes.

### CAMBIOS REQUERIDOS:

#### 1. Reemplazar `Chatbot.py` (entry point principal)
Transformarlo en `Tutor.py` o modificar `Chatbot.py` para que sea el 
tutor RAG principal con:
- Selector de asignatura en sidebar (circuitos, electrónica, máquinas eléctricas)
- Selector de proveedor LLM: OpenAI, Anthropic, Google Gemini, Ollama (local)
- Campo de API key dinámico según proveedor seleccionado (ocultar si es Ollama)
- Chat interface con historial usando `st.session_state`
- Respuestas basadas en RAG usando ChromaDB como vector store
- System prompt de tutor con scope controlado por asignatura seleccionada

#### 2. Crear estructura de carpetas nueva dentro del proyecto

core/
├── _init_.py
├── llm_factory.py ← Abstracción multi-proveedor
├── rag_pipeline.py ← ConversationalRetrievalChain con system prompt tutor
└── vector_store.py ← ChromaDB: ingestión y retrieval

content/
└── asignaturas/
├── circuitos/ ← carpeta vacía con .gitkeep
├── electronica/ ← carpeta vacía con .gitkeep
└── maquinas_electricas/ ← carpeta vacía con .gitkeep

.streamlit/
└── secrets.toml.example ← Template con keys vacías (NO el real)


#### 3. Modificar `pages/` — reemplazar páginas existentes
- **Eliminar**: `3_Langchain_Quickstart.py`, `4_Langchain_PromptTemplate.py`, 
  `5_Chat_with_user_feedback.py` (obsoletas para este propósito)
- **Mantener y adaptar**: `1_File_Q&A.py` → renombrar a `1_Cargar_Contenido.py`
  para subir PDFs por asignatura e ingresarlos a ChromaDB
- **Crear nueva**: `2_Configuracion.py` para gestionar API keys y modelo Ollama URL

#### 4. Actualizar `requirements.txt`
Reemplazar el contenido actual con:

streamlit>=1.32
langchain>=0.1.0
langchain-community>=0.0.20
langchain-openai>=0.0.5
langchain-anthropic>=0.1.0
langchain-google-genai>=0.0.6
langchain-ollama>=0.1.0
chromadb>=0.4.0
pypdf>=3.0.0
unstructured>=0.10.0
python-dotenv>=1.0.0


---

### ESPECIFICACIONES DE CÓDIGO:

#### `core/llm_factory.py`
```python
# Debe soportar estos 4 proveedores con interfaz unificada:
# - "OpenAI": modelos gpt-4o, gpt-4o-mini, gpt-3.5-turbo
# - "Anthropic": claude-3-5-sonnet-20241022, claude-3-haiku-20240307
# - "Google": gemini-2.0-flash, gemini-1.5-pro
# - "Ollama": llama3, mistral, phi3 (base_url configurable, default localhost:11434)
# Función principal: get_llm(provider, model, api_key, ollama_url) -> BaseChatModel
```

#### `core/rag_pipeline.py`
```python
# System prompt del tutor debe incluir:
# - Rol: "Eres un tutor experto en Ingeniería Eléctrica"
# - Scope dinámico: variable {asignatura} con temas definidos por asignatura
# - Instrucción de scope: si la pregunta está fuera del contenido cargado, 
#   indicar que no corresponde al material de la asignatura
# - Idioma: responder siempre en español
# - Pedagogía: explicar con ejemplos, paso a paso cuando sea necesario
# - Contexto RAG: incorporar {context} del retriever
# Usar: ConversationalRetrievalChain con memory y source_documents=True
# Mostrar fuentes (nombre del PDF) al final de cada respuesta
```

#### `core/vector_store.py`
```python
# ChromaDB persistente en ./chroma_db/ (excluir de git)
# Colecciones separadas por asignatura: "circuitos", "electronica", "maquinas"
# Función ingest_documents(pdf_files, asignatura) -> int (nro chunks indexados)
# Función get_retriever(asignatura, k=4) -> BaseRetriever
# Embeddings: usar OpenAI text-embedding-3-small por defecto,
#             con fallback a HuggingFaceEmbeddings("all-MiniLM-L6-v2") si no hay key
```

#### `pages/1_Cargar_Contenido.py`
```python
# UI para subir PDFs con:
# - st.file_uploader(accept_multiple_files=True, type=["pdf"])
# - Selector de asignatura destino
# - Botón "Indexar en ChromaDB"
# - Mostrar progreso con st.progress() y st.status()
# - Mostrar número de chunks indexados al finalizar
# - Listar documentos ya indexados por asignatura
```

---

### RESTRICCIONES IMPORTANTES:
1. Mantener compatibilidad con `.devcontainer/` existente
2. Agregar `chroma_db/` y `.streamlit/secrets.toml` al `.gitignore`
3. Todo el código debe tener docstrings en español
4. Los mensajes de la UI deben estar en español
5. Manejar excepciones para: API key inválida, Ollama no disponible, 
   sin documentos indexados para la asignatura seleccionada
6. El archivo `app_test.py` existente debe actualizarse con al menos 
   2 tests básicos para `llm_factory.py` y `vector_store.py`

### ORDEN DE IMPLEMENTACIÓN SUGERIDO:
1. Actualizar `requirements.txt`
2. Crear estructura de carpetas y `__init__.py`
3. Implementar `core/llm_factory.py`
4. Implementar `core/vector_store.py`
5. Implementar `core/rag_pipeline.py`
6. Modificar `Chatbot.py` (entry point)
7. Crear `pages/1_Cargar_Contenido.py`
8. Crear `pages/2_Configuracion.py`
9. Actualizar `.gitignore`
10. Actualizar `app_test.py`

