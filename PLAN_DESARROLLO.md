<![CDATA[<meta charset="UTF-8">

<style>
  body, h1, h2, h3, h4, p, li, td, th, code, pre, span, div {
    font-family: "Consolas", "Courier New", monospace !important;
  }

  h1 { color: #4a7c20; border-bottom: 3px solid #95f651; padding-bottom: 8px; }
  h2 { color: #2e6b50; border-left: 5px solid #95f651; padding-left: 12px; margin-top: 32px; }
  h3 { color: #1a5c45; border-left: 3px solid #baf3d7; padding-left: 10px; }
  h4 { color: #2e6b50; }

  code {
    background-color: #cbf4e8;
    color: #1a3d2b;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "Consolas", monospace !important;
  }

  pre {
    background-color: #cbeff6;
    border-left: 4px solid #95f651;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
  }

  pre code {
    background-color: transparent;
    padding: 0;
    color: #1a2e20;
  }

  table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
  }

  th {
    background-color: #95f651;
    color: #1a2e20;
    padding: 10px 14px;
    text-align: left;
  }

  td {
    background-color: #ecfdef;
    padding: 8px 14px;
    border-bottom: 1px solid #baf3d7;
  }

  tr:nth-child(even) td { background-color: #cbf4e8; }

  blockquote {
    background-color: #ecfdef;
    border-left: 5px solid #baf3d7;
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 0 6px 6px 0;
    color: #2e6b50;
  }

  .badge-critico    { background:#95f651; color:#1a2e20; padding:2px 8px; border-radius:12px; font-weight:bold; }
  .badge-alto       { background:#baf3d7; color:#1a3d2b; padding:2px 8px; border-radius:12px; font-weight:bold; }
  .badge-medio      { background:#cbeff6; color:#1a3d2b; padding:2px 8px; border-radius:12px; font-weight:bold; }
  .badge-bajo       { background:#ecfdef; color:#1a3d2b; padding:2px 8px; border-radius:12px; font-weight:bold; }
</style>

---

# ⚡ PLAN INTEGRAL DE DESARROLLO
# Tutor RAG · Ingeniería Eléctrica
### Repositorio: `YnnySA/tutor-agent-ciruitpro`

---

## 📋 Índice

1. [Estado Real del Proyecto](#estado-real)
2. [Arquitectura Objetivo](#arquitectura-objetivo)
3. [Fase 1 — Correcciones Críticas de Infraestructura](#fase-1)
4. [Fase 2 — Capa de Configuración Externa](#fase-2)
5. [Fase 3 — Refactorizar Backend](#fase-3)
6. [Fase 4 — Refactorizar Frontend](#fase-4)
7. [Fase 5 — CLI de Indexación](#fase-5)
8. [Fase 6 — Limpieza y Tests](#fase-6)
9. [Flujo Operativo con PDF del Cliente](#flujo-operativo)
10. [Resumen Ejecutivo](#resumen)

---

## 1. Estado Real del Proyecto {#estado-real}

> Inventario completo de archivos actuales con su nivel de deuda técnica.

| Archivo | Estado | Problema detectado | Prioridad |
|---|---|---|---|
| `llm-examples/Chatbot.py` | ✅ Funcional | Mezcla UI + lógica de negocio + manejo errores | 🔴 Crítico |
| `core/llm_factory.py` | ✅ Sólido | `PROVIDER_MODELS` hardcodeado en código | 🟡 Medio |
| `core/rag_pipeline.py` | ✅ Funcional | `TEMARIO_ASIGNATURA` hardcodeado, chain deprecated | 🟠 Alto |
| `core/vector_store.py` | ⚠️ Incompleto | Solo soporta upload dinámico de Streamlit | 🔴 Crítico |
| `pages/1_Cargar_Contenido.py` | ❌ Incompatible | Estudiantes suben docs — modelo de negocio incorrecto | 🔴 Eliminar |
| `pages/2_Configuracion.py` | ✅ OK | Sin protección admin | 🟢 Bajo |
| `requirements.txt` | ⚠️ Desactualizado | `langchain>=0.1.0` obsoleto para 2026 | 🟠 Alto |
| `scripts/index_docs.py` | ❌ No existe | Crítico para indexar PDF del cliente | 🔴 Crítico |
| Estructura raíz del repo | ❌ Anidada | Todo dentro de `llm-examples/`, rompe Streamlit Cloud | 🔴 Crítico |

---

## 2. Arquitectura Objetivo {#arquitectura-objetivo}

> **Principio rector:** Todo lo que cambia por configuración → `config/` · Todo lo visual → `frontend/` · Toda la lógica → `backend/`

```
tutor-agent-ciruitpro/               ← RAÍZ LIMPIA
│
├── Chatbot.py                        ← Entry point (~30 líneas, solo UI)
│
├── 📁 frontend/                      ← Todo Streamlit, sin lógica de negocio
│   ├── __init__.py
│   ├── state.py                      ← st.session_state centralizado
│   ├── sidebar.py                    ← Componente sidebar reutilizable
│   └── components/
│       ├── chat.py                   ← Render del chat + historial
│       └── source_badge.py          ← Muestra fuentes RAG al estudiante
│
├── 📁 backend/                       ← Lógica pura, CERO imports de streamlit
│   ├── __init__.py
│   ├── llm_factory.py                ← Fábrica multi-proveedor (lee config/)
│   ├── rag_pipeline.py               ← Chain RAG conversacional (lee config/)
│   ├── vector_store.py               ← ChromaDB: ingest_from_directory + retrieval
│   └── indexer.py                    ← NUEVO: orquesta indexación desde directorios
│
├── 📁 config/                        ← TODO lo editable sin tocar código Python
│   ├── asignaturas.yaml              ← Asignaturas, temarios, rutas de PDFs
│   ├── providers.yaml                ← Proveedores LLM y modelos disponibles
│   └── settings.yaml                 ← chunk_size, k, temperatura, paths
│
├── 📁 pages/                         ← Solo admin, no visible para estudiantes
│   └── 2_Configuracion.py           ← API keys (refactorizado)
│
├── 📁 content/
│   └── asignaturas/
│       ├── circuitos/                ← PDFs del cliente van aquí
│       ├── electronica/
│       └── maquinas_electricas/
│
├── 📁 scripts/
│   └── index_docs.py                 ← CLI: ejecutar una vez por semestre
│
├── 📁 tests/
│   ├── test_llm_factory.py
│   ├── test_vector_store.py
│   └── test_rag_pipeline.py
│
├── chroma_db/                        ← Generado localmente (.gitignore)
├── requirements.txt                  ← Versiones actualizadas 2026
├── instrucciones.md                  ← Conservar
├── PLAN_DESARROLLO.md                ← Este archivo
├── .streamlit/
│   ├── secrets.toml                  ← API keys reales (.gitignore)
│   └── secrets.toml.example         ← Template seguro (en repo)
└── .gitignore
```

---

## 3. FASE 1 — Correcciones Críticas de Infraestructura {#fase-1}

> <span class="badge-critico">🔴 PRIORIDAD CRÍTICA</span> · Duración estimada: **20 minutos**
> Sin esta fase, el resto no funciona correctamente en Streamlit Cloud.

### 1.1 Desanidar el proyecto

```bash
# Desde ~/Documents/LLM (raíz del repo)
cp -r llm-examples/. .
rm -rf llm-examples/

# Verificar que Chatbot.py está en la raíz
ls Chatbot.py   # debe existir
```

### 1.2 Actualizar `.gitignore`

```gitignore
# Índice vectorial generado localmente
chroma_db/

# API keys reales
.streamlit/secrets.toml

# PDFs del cliente (propiedad intelectual)
content/asignaturas/**/*.pdf

# Python
__pycache__/
*.pyc
*.pyo
.env
venv/
.venv/
```

### 1.3 Actualizar `requirements.txt`

```text
streamlit>=1.40
langchain>=0.3.0
langchain-community>=0.3.0
langchain-openai>=0.2.0
langchain-anthropic>=0.3.0
langchain-google-genai>=2.0.0
langchain-ollama>=0.2.0
chromadb>=0.5.0
pypdf>=4.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

### 1.4 Commit y push

```bash
git add .
git commit -m "refactor: mover proyecto a raíz y actualizar dependencias"
git push
```

---

## 4. FASE 2 — Capa de Configuración Externa {#fase-2}

> <span class="badge-critico">🔴 PRIORIDAD CRÍTICA</span> · Duración estimada: **15 minutos**
> Debe completarse antes de modificar cualquier archivo Python.

### 4.1 `config/asignaturas.yaml`

```yaml
# Editar aquí para agregar/modificar asignaturas SIN tocar código Python
asignaturas:
  circuitos:
    nombre_display: "Circuitos Eléctricos"
    collection_id: "circuitos"
    pdf_dir: "content/asignaturas/circuitos"
    temario: >
      Leyes de Kirchhoff, análisis nodal y de mallas,
      teoremas de Thevenin y Norton, respuesta transitoria RC/RL/RLC,
      potencia en AC, factor de potencia y corrección.

  electronica:
    nombre_display: "Electrónica"
    collection_id: "electronica"
    pdf_dir: "content/asignaturas/electronica"
    temario: >
      Diodos rectificadores y Zener, transistores BJT y MOSFET,
      amplificadores operacionales, polarización DC,
      modelos de pequeña señal, electrónica digital básica.

  maquinas_electricas:
    nombre_display: "Máquinas Eléctricas"
    collection_id: "maquinas"
    pdf_dir: "content/asignaturas/maquinas_electricas"
    temario: >
      Transformadores monofásicos y trifásicos, máquinas DC
      (motores y generadores), máquinas síncronas y asíncronas,
      circuitos equivalentes, ensayos normalizados IEC,
      regulación de tensión y rendimiento.
```

### 4.2 `config/providers.yaml`

```yaml
# Agregar nuevos modelos aquí sin modificar backend/llm_factory.py
providers:
  OpenAI:
    modelos: ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    requiere_key: true
    key_env: "OPENAI_API_KEY"

  Anthropic:
    modelos: ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    requiere_key: true
    key_env: "ANTHROPIC_API_KEY"

  Google:
    modelos: ["gemini-2.0-flash", "gemini-1.5-pro"]
    requiere_key: true
    key_env: "GOOGLE_API_KEY"

  Ollama:
    modelos: ["qwen3.5:4b", "llama3.1:8b", "mistral:7b", "phi3:mini"]
    requiere_key: false
    default_url: "http://localhost:11434"
```

### 4.3 `config/settings.yaml`

```yaml
rag:
  chunk_size: 1000
  chunk_overlap: 150
  retrieval_k: 4
  embeddings_model: "text-embedding-3-small"        # OpenAI (preferido)
  embeddings_fallback: "all-MiniLM-L6-v2"           # HuggingFace (sin key)

llm:
  temperature: 0.2

index:
  auto_index_on_startup: true    # indexa automáticamente si hay PDFs nuevos
  persist_dir: "chroma_db"
  content_base: "content/asignaturas"
```

---

## 5. FASE 3 — Refactorizar Backend {#fase-3}

> <span class="badge-alto">🟠 PRIORIDAD ALTA</span> · Duración estimada: **30 minutos**

### 5.1 Renombrar `core/` → `backend/`

```bash
mv core/ backend/
# Actualizar imports en todos los archivos:
# "from core." → "from backend."
```

### 5.2 `backend/vector_store.py` — agregar `ingest_from_directory()`

```python
def ingest_from_directory(
    asignatura: str,
    openai_api_key: str | None = None,
    force_reindex: bool = False,
) -> int:
    """
    Lee todos los PDFs desde config/asignaturas.yaml[asignatura][pdf_dir]
    y los indexa en ChromaDB. Si force_reindex=True, limpia y reconstruye.
    Retorna número de chunks indexados.
    """
    config = _load_settings()
    pdf_dir = Path(config["asignaturas"][asignatura]["pdf_dir"])
    pdfs = list(pdf_dir.glob("*.pdf"))

    if not pdfs:
        raise FileNotFoundError(
            f"No hay PDFs en '{pdf_dir}'. "
            f"Coloca el material del cliente ahí antes de indexar."
        )

    if force_reindex:
        _drop_collection(asignatura)

    documentos = []
    for pdf_path in pdfs:
        loader = PyPDFLoader(str(pdf_path))
        for doc in loader.load():
            doc.metadata["source"]     = pdf_path.name
            doc.metadata["asignatura"] = asignatura
            documentos.append(doc)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["rag"]["chunk_size"],
        chunk_overlap=config["rag"]["chunk_overlap"],
    )
    chunks = splitter.split_documents(documentos)
    vs = _get_vector_store(asignatura, openai_api_key)
    vs.add_documents(chunks)
    vs.persist()
    return len(chunks)
```

### 5.3 `backend/indexer.py` — NUEVO archivo

```python
"""Orquestador de indexación — sin dependencias de Streamlit."""
import yaml
from pathlib import Path
from backend.vector_store import ingest_from_directory, _get_vector_store

def load_asignaturas() -> dict:
    with open("config/asignaturas.yaml") as f:
        return yaml.safe_load(f)["asignaturas"]

def index_asignatura(asig_id: str, force: bool = False) -> int:
    return ingest_from_directory(asig_id, force_reindex=force)

def index_all(force: bool = False) -> dict[str, int | str]:
    resultados = {}
    for asig_id in load_asignaturas():
        try:
            resultados[asig_id] = index_asignatura(asig_id, force)
        except FileNotFoundError:
            resultados[asig_id] = "sin PDFs aún"
    return resultados

def chroma_status() -> dict[str, int]:
    """Retorna número de chunks por asignatura en ChromaDB."""
    status = {}
    for asig_id in load_asignaturas():
        vs = _get_vector_store(asig_id)
        status[asig_id] = vs._collection.count()
    return status
```

### 5.4 `backend/rag_pipeline.py` — leer temario desde `config/`

```python
# ANTES (hardcodeado)
TEMARIO_ASIGNATURA = {
    "circuitos": "leyes de Kirchhoff...",
    ...
}

# DESPUÉS (desde config/asignaturas.yaml)
import yaml

def _get_temario(asignatura: str) -> str:
    with open("config/asignaturas.yaml") as f:
        data = yaml.safe_load(f)
    return data["asignaturas"][asignatura]["temario"]
```

### 5.5 `backend/llm_factory.py` — leer modelos desde `config/`

```python
# ANTES
PROVIDER_MODELS = {"OpenAI": ["gpt-4o", ...], ...}

# DESPUÉS
import yaml

def load_providers() -> dict:
    with open("config/providers.yaml") as f:
        return yaml.safe_load(f)["providers"]

def get_provider_models() -> dict[str, list[str]]:
    return {k: v["modelos"] for k, v in load_providers().items()}
```

---

## 6. FASE 4 — Refactorizar Frontend {#fase-4}

> <span class="badge-medio">🟡 PRIORIDAD MEDIA</span> · Duración estimada: **25 minutos**

### 6.1 `frontend/state.py`

```python
"""Gestión centralizada de st.session_state — sin lógica de negocio."""
import streamlit as st

def inicializar_estado() -> None:
    st.session_state.setdefault("tutor_messages", [{
        "role": "assistant",
        "content": "Hola, soy tu tutor de Ingeniería Eléctrica. ¿Qué deseas consultar?"
    }])
    st.session_state.setdefault("tutor_chain", None)
    st.session_state.setdefault("tutor_chain_config", None)
    st.session_state.setdefault("tutor_config", _load_secrets())

def _load_secrets() -> dict:
    try:
        return {k: st.secrets.get(k, "") for k in
                ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "OLLAMA_URL"]}
    except Exception:
        return {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "",
                "GOOGLE_API_KEY": "", "OLLAMA_URL": "http://localhost:11434"}
```

### 6.2 `Chatbot.py` — resultado final (solo UI)

```python
"""Entry point — orquesta UI sin lógica de negocio."""
import streamlit as st
from frontend.state import inicializar_estado
from frontend.sidebar import render_sidebar
from frontend.components.chat import render_chat, handle_input

st.set_page_config(
    page_title="Tutor · Ingeniería Eléctrica",
    page_icon="⚡",
    layout="centered"
)

inicializar_estado()
config = render_sidebar()   # retorna: provider, model, asignatura, api_key
render_chat()               # renderiza historial desde session_state
handle_input(config)        # captura prompt → llama backend → guarda respuesta
```

### 6.3 Eliminar `pages/1_Cargar_Contenido.py`

```bash
git rm pages/1_Cargar_Contenido.py
git commit -m "feat: eliminar página de carga de docs (indexación vía CLI)"
```

---

## 7. FASE 5 — CLI de Indexación {#fase-5}

> <span class="badge-alto">🟠 PRIORIDAD ALTA</span> · Duración estimada: **10 minutos**
> Este script debe estar listo **antes** de recibir el PDF del cliente.

### `scripts/index_docs.py`

```python
"""
CLI para indexar PDFs del cliente en ChromaDB.

Uso:
  python scripts/index_docs.py --status
  python scripts/index_docs.py --asignatura circuitos
  python scripts/index_docs.py --all
  python scripts/index_docs.py --asignatura circuitos --force
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.indexer import index_all, index_asignatura, chroma_status

parser = argparse.ArgumentParser(
    description="Indexador de documentos para Tutor RAG · Ingeniería Eléctrica"
)
parser.add_argument("--asignatura", help="ID de la asignatura (circuitos | electronica | maquinas_electricas)")
parser.add_argument("--all",    action="store_true", help="Indexar todas las asignaturas")
parser.add_argument("--force",  action="store_true", help="Reindexar desde cero (borra colección existente)")
parser.add_argument("--status", action="store_true", help="Ver estado actual de ChromaDB")
args = parser.parse_args()

if args.status:
    print("\n📊 Estado de ChromaDB:")
    for asig, n in chroma_status().items():
        icon = "✅" if n > 0 else "⚪"
        print(f"  {icon}  {asig}: {n} chunks indexados")

elif args.all:
    print("\n🔄 Indexando todas las asignaturas...")
    for asig, resultado in index_all(force=args.force).items():
        icon = "✅" if isinstance(resultado, int) else "⚠️ "
        print(f"  {icon}  {asig}: {resultado}")

elif args.asignatura:
    print(f"\n🔄 Indexando '{args.asignatura}'...")
    n = index_asignatura(args.asignatura, force=args.force)
    print(f"  ✅  {args.asignatura}: {n} chunks indexados")

else:
    parser.print_help()
```

---

## 8. FASE 6 — Limpieza y Tests {#fase-6}

> <span class="badge-bajo">🔵 PRIORIDAD BAJA</span> · Duración estimada: **30 minutos**
> Completar después de validar funcionamiento end-to-end.

### Tests mínimos requeridos

```python
# tests/test_llm_factory.py
def test_provider_models_from_config():
    from backend.llm_factory import get_provider_models
    models = get_provider_models()
    assert "OpenAI" in models
    assert "Ollama" in models

# tests/test_vector_store.py
def test_ingest_from_directory_sin_pdfs(tmp_path):
    with pytest.raises(FileNotFoundError):
        ingest_from_directory("circuitos")

# tests/test_rag_pipeline.py
def test_temario_desde_config():
    temario = _get_temario("circuitos")
    assert "Kirchhoff" in temario
```

---

## 9. Flujo Operativo cuando llegue el PDF {#flujo-operativo}

```
CLIENTE ENTREGA PDF
      │
      ▼
1. Copiar PDF al directorio correcto:
   cp ~/Downloads/circuitos.pdf content/asignaturas/circuitos/
      │
      ▼
2. Verificar estado actual:
   python scripts/index_docs.py --status
      │
      ▼
3. Indexar (primera vez):
   python scripts/index_docs.py --asignatura circuitos
      │
      ▼
4. Verificar resultado:
   python scripts/index_docs.py --status
   ✅  circuitos: 847 chunks indexados
      │
      ▼
5. Lanzar la aplicación:
   streamlit run Chatbot.py
      │
      ▼
6. ESTUDIANTES YA PUEDEN CONSULTAR ✅

─────────────────────────────────────
CUANDO EL CLIENTE ACTUALICE EL PDF:
─────────────────────────────────────
cp ~/Downloads/circuitos_v2.pdf content/asignaturas/circuitos/
python scripts/index_docs.py --asignatura circuitos --force
✅  circuitos: 1024 chunks indexados (reindexado desde cero)
```

---

## 10. Resumen Ejecutivo {#resumen}

| Fase | Tarea Principal | Tiempo | Prioridad |
|---|---|---|---|
| **1** | Desanidar repo + actualizar `requirements.txt` | 20 min | 🔴 Inmediata |
| **2** | Crear `config/asignaturas.yaml`, `providers.yaml`, `settings.yaml` | 15 min | 🔴 Antes de código |
| **3** | `core/` → `backend/` + agregar `indexer.py` + leer desde config | 30 min | 🟠 Esta semana |
| **4** | Crear `frontend/` + limpiar `Chatbot.py` + eliminar página upload | 25 min | 🟡 Esta semana |
| **5** | `scripts/index_docs.py` CLI | 10 min | 🟠 Antes del PDF |
| **6** | Tests en `tests/` | 30 min | 🔵 Post-funcional |

> **Total estimado:** ~2.5 horas · Con GitHub Copilot CLI: ~45 minutos

---

### Paleta de Colores del Proyecto

| Nombre | HEX | Uso |
|---|---|---|
| Lawn Green | `#95f651` | Acentos primarios, bordes activos, badges críticos |
| Celadon | `#baf3d7` | Bordes secundarios, highlights |
| Light Cyan | `#cbeff6` | Fondos de código (`pre`) |
| Frozen Water | `#cbf4e8` | Fondos de código inline (`code`), filas pares de tabla |
| Honeydew | `#ecfdef` | Fondo general de celdas, blockquotes |

> Fuente del proyecto: **Consolas** (monoespaciada) para todo el documento y la aplicación.

---

*Generado: 2026-07-22 · Repositorio: [YnnySA/tutor-agent-ciruitpro](https://github.com/YnnySA/tutor-agent-ciruitpro)*
]]>