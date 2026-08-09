"""Módulo de internacionalización (i18n) para el Tutor RAG."""

from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        # --- Página principal ---
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
    },
    "en": {
        # --- Main page ---
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
    },
}

LANGUAGE_OPTIONS: dict[str, str] = {
    "Español": "es",
    "English": "en",
}


def get_translations(lang: str) -> dict[str, str]:
    """Retorna el diccionario de traducciones para el idioma dado."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"])
