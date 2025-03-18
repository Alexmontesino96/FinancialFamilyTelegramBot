"""
Módulo de idiomas para el bot

Este módulo proporciona soporte para múltiples idiomas en el bot.
"""

from languages.utils.translator import (
    get_message, 
    set_language, 
    get_supported_languages, 
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE
)
from languages.utils.language_handler import get_language_handlers

__all__ = [
    'get_message',
    'set_language',
    'get_supported_languages',
    'SUPPORTED_LANGUAGES',
    'DEFAULT_LANGUAGE',
    'get_language_handlers'
] 