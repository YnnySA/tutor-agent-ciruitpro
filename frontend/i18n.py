"""Módulo de internacionalización (i18n) para el Tutor RAG."""

from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        # --- Página principal (Chatbot) ---
        "page_title": "Tutor RAG de Ingeniería Eléctrica",
        "app_title": "Tutor RAG de Ingeniería Eléctrica",
        "app_caption": "Responde con base en el contenido indexado por asignatura",
        "welcome_message": (
            "Hola, soy tu tutor de Ingeniería Eléctrica. "
            "Haz una pregunta sobre la asignatura seleccionada."
        ),
        "chat_placeholder": "Escribe tu pregunta del material cargado",
        # --- Sidebar ---
        "sidebar_title": "Configuración del tutor",
        "label_course": "Asignatura",
        "label_provider": "Proveedor LLM",
        "label_model": "Modelo",
        "label_api_key": "API key de",
        "label_ollama_url": "URL de Ollama",
        "ollama_info": "Para Ollama no se requiere API key.",
        "ollama_help": "Ejemplo: http://localhost:11434",
        "language_label": "Idioma / Language",
        # --- Errores ---
        "error_no_api_key": "Agrega tu API key de {provider} para continuar.",
        "error_invalid_key": "La API key es inválida o no tiene permisos para el modelo seleccionado.",
        "error_ollama_connection": (
            "No fue posible conectarse con Ollama. "
            "Verifica que esté activo y que la URL sea correcta."
        ),
        "error_generic": "Ocurrió un error al generar la respuesta: {raw}",
        # --- Fuentes ---
        "sources_label": "Fuentes",
        "sources_unavailable": "No disponibles.",
        # --- Página Upload Content ---
        "upload_page_title": "Cargar contenido para el tutor",
        "upload_page_caption": "Sube PDFs y asócialos a una asignatura para indexarlos en ChromaDB",
        "label_target_course": "Asignatura destino",
        "label_select_pdfs": "Selecciona uno o varios PDFs",
        "btn_index": "Indexar en ChromaDB",
        "warn_no_files": "Primero debes cargar al menos un archivo PDF.",
        "status_indexing": "Indexando documentos...",
        "status_processing": "Procesando:",
        "status_done": "Indexación completada",
        "success_indexed": "Se indexaron {chunks} chunks en la asignatura '{course}'.",
        "subheader_indexed_docs": "Documentos indexados",
        "info_no_docs": "Aún no hay documentos indexados para esta asignatura.",
        # --- Página Settings ---
        "settings_page_title": "Configuración del tutor",
        "settings_page_caption": "Guarda tus credenciales de proveedores y la URL de Ollama",
        "label_openai_key": "API key de OpenAI",
        "label_anthropic_key": "API key de Anthropic",
        "label_google_key": "API key de Google",
        "btn_save_settings": "Guardar configuración",
        "success_settings_saved": "Configuración guardada en la sesión actual.",
        "info_secrets_hint": (
            "Para persistir claves fuera de la sesión, usa `.streamlit/secrets.toml` "
            "a partir del template `secrets.toml.example`."
        ),
    },
    "en": {
        # --- Main page (Chatbot) ---
        "page_title": "Electrical Engineering RAG Tutor",
        "app_title": "Electrical Engineering RAG Tutor",
        "app_caption": "Answers based on course-specific indexed content",
        "welcome_message": (
            "Hi, I'm your Electrical Engineering tutor. "
            "Ask a question about the selected course."
        ),
        "chat_placeholder": "Type your question based on the uploaded material",
        # --- Sidebar ---
        "sidebar_title": "Tutor configuration",
        "label_course": "Course",
        "label_provider": "LLM provider",
        "label_model": "Model",
        "label_api_key": "API key for",
        "label_ollama_url": "Ollama URL",
        "ollama_info": "No API key required for Ollama.",
        "ollama_help": "Example: http://localhost:11434",
        "language_label": "Language / Idioma",
        # --- Errors ---
        "error_no_api_key": "Add your {provider} API key to continue.",
        "error_invalid_key": "The API key is invalid or does not have permission for the selected model.",
        "error_ollama_connection": (
            "Could not connect to Ollama. "
            "Make sure it is running and the URL is correct."
        ),
        "error_generic": "An error occurred while generating the response: {raw}",
        # --- Sources ---
        "sources_label": "Sources",
        "sources_unavailable": "Not available.",
        # --- Upload Content page ---
        "upload_page_title": "Upload content for the tutor",
        "upload_page_caption": "Upload PDFs and associate them with a course to index in ChromaDB",
        "label_target_course": "Target course",
        "label_select_pdfs": "Select one or more PDFs",
        "btn_index": "Index in ChromaDB",
        "warn_no_files": "You must upload at least one PDF file first.",
        "status_indexing": "Indexing documents...",
        "status_processing": "Processing:",
        "status_done": "Indexing complete",
        "success_indexed": "Successfully indexed {chunks} chunks for course '{course}'.",
        "subheader_indexed_docs": "Indexed documents",
        "info_no_docs": "No documents indexed yet for this course.",
        # --- Settings page ---
        "settings_page_title": "Tutor settings",
        "settings_page_caption": "Save your provider credentials and Ollama URL",
        "label_openai_key": "OpenAI API key",
        "label_anthropic_key": "Anthropic API key",
        "label_google_key": "Google API key",
        "btn_save_settings": "Save settings",
        "success_settings_saved": "Settings saved for the current session.",
        "info_secrets_hint": (
            "To persist keys beyond the session, use `.streamlit/secrets.toml` "
            "based on the `secrets.toml.example` template."
        ),
    },
}

LANGUAGE_OPTIONS: dict[str, str] = {
    "Español": "es",
    "English": "en",
}


def get_translations(lang: str) -> dict[str, str]:
    """Returns the translation dictionary for the given language."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"])
