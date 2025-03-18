"""
Sistema de traducción para el bot

Este módulo proporciona las funcionalidades para manejar múltiples idiomas en el bot.
"""

from typing import Dict, Optional, Any, Type
import os
import importlib

# Idiomas soportados
SUPPORTED_LANGUAGES = {
    "es": "Español",
    "en": "English",
    "fr": "Français"
}

# Mapeo de códigos de idioma del bot a la API
BOT_TO_API_LANGUAGE = {
    "es": "ES",
    "en": "EN",
    "fr": "FR"
}

# Mapeo de códigos de idioma de la API al bot
API_TO_BOT_LANGUAGE = {
    "ES": "es",
    "EN": "en",
    "FR": "fr"
}

# Idioma por defecto
DEFAULT_LANGUAGE = "es"

class LanguageManager:
    """
    Gestor de idiomas para el bot.
    
    Esta clase maneja la carga de mensajes en diferentes idiomas y proporciona
    acceso a los textos traducidos.
    """
    
    _instance = None  # Singleton instance
    _messages_cache: Dict[str, Any] = {}  # Cache para los módulos de mensajes cargados
    
    def __new__(cls):
        """Implementación del patrón singleton."""
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        """Inicialización del gestor de idiomas."""
        self._user_languages = {}  # Mapeo de user_id a código de idioma
    
    def get_user_language(self, user_id: str) -> str:
        """
        Obtiene el código de idioma para un usuario.
        
        Args:
            user_id: ID del usuario en Telegram.
            
        Returns:
            Código de idioma (ej: 'es', 'en').
        """
        return self._user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    def set_user_language(self, user_id: str, language_code: str) -> bool:
        """
        Establece el idioma preferido para un usuario localmente.
        
        Args:
            user_id: ID del usuario en Telegram.
            language_code: Código del idioma a establecer.
            
        Returns:
            True si se estableció correctamente, False si el idioma no es soportado.
        """
        if language_code in SUPPORTED_LANGUAGES:
            self._user_languages[user_id] = language_code
            return True
        return False
    
    def get_messages(self, language_code: Optional[str] = None) -> Any:
        """
        Obtiene el módulo de mensajes para un idioma específico.
        
        Args:
            language_code: Código del idioma. Si es None, se usa el idioma por defecto.
            
        Returns:
            Clase de mensajes para el idioma especificado.
        """
        if language_code is None:
            language_code = DEFAULT_LANGUAGE
            
        # Si el idioma no es soportado, usar el idioma por defecto
        if language_code not in SUPPORTED_LANGUAGES:
            language_code = DEFAULT_LANGUAGE
            
        # Verificar si ya está en caché
        if language_code in self._messages_cache:
            return self._messages_cache[language_code]
            
        try:
            # Importar dinámicamente el módulo de mensajes
            module = importlib.import_module(f"languages.{language_code}.messages")
            messages_class = module.Messages
            
            # Guardar en caché
            self._messages_cache[language_code] = messages_class
            
            return messages_class
        except (ImportError, AttributeError) as e:
            print(f"Error cargando mensajes para idioma {language_code}: {str(e)}")
            # Si hay un error, intentar cargar el idioma por defecto
            if language_code != DEFAULT_LANGUAGE:
                return self.get_messages(DEFAULT_LANGUAGE)
            # Si incluso el idioma por defecto falla, lanzar una excepción
            raise ImportError(f"No se pudo cargar el módulo de mensajes para ningún idioma.")
    
    def get_message_for_user(self, user_id: str, message_key: str, **kwargs) -> str:
        """
        Obtiene un mensaje traducido para un usuario específico.
        
        Args:
            user_id: ID del usuario en Telegram.
            message_key: Clave del mensaje a obtener.
            **kwargs: Parámetros para formatear el mensaje.
            
        Returns:
            Mensaje traducido y formateado.
        """
        language_code = self.get_user_language(user_id)
        messages = self.get_messages(language_code)
        
        try:
            message_template = getattr(messages, message_key)
            # Formatear el mensaje con los parámetros proporcionados
            return message_template.format(**kwargs) if kwargs else message_template
        except (AttributeError, KeyError) as e:
            print(f"Error obteniendo mensaje '{message_key}' para idioma {language_code}: {str(e)}")
            # Intentar con el idioma por defecto
            if language_code != DEFAULT_LANGUAGE:
                default_messages = self.get_messages(DEFAULT_LANGUAGE)
                try:
                    message_template = getattr(default_messages, message_key)
                    return message_template.format(**kwargs) if kwargs else message_template
                except (AttributeError, KeyError):
                    pass
            
            # Si todo falla, devolver un mensaje genérico
            return f"Message not found: {message_key}"

# Crear una instancia global del gestor de idiomas
translator = LanguageManager()

def get_message(user_id: str, message_key: str, **kwargs) -> str:
    """
    Función de conveniencia para obtener un mensaje traducido.
    
    Args:
        user_id: ID del usuario en Telegram.
        message_key: Clave del mensaje a obtener.
        **kwargs: Parámetros para formatear el mensaje.
        
    Returns:
        Mensaje traducido y formateado.
    """
    return translator.get_message_for_user(user_id, message_key, **kwargs)

def set_language(user_id: str, language_code: str) -> bool:
    """
    Función para establecer el idioma de un usuario y sincronizarlo con la API.
    
    Args:
        user_id: ID del usuario en Telegram.
        language_code: Código del idioma a establecer (en minúsculas: es, en, fr).
        
    Returns:
        True si se estableció correctamente, False si el idioma no es soportado.
    """
    # Establecer el idioma localmente
    local_success = translator.set_user_language(user_id, language_code)
    
    # Si se estableció correctamente, actualizar también en la API
    if local_success:
        try:
            # Importar aquí para evitar dependencias circulares
            from services.member_service import MemberService
            
            # Convertir el código de idioma al formato de la API (mayúsculas)
            api_language_code = BOT_TO_API_LANGUAGE.get(language_code)
            
            # Primero, obtener el UUID del miembro a partir del telegram_id
            status_code, member = MemberService.get_member(user_id)
            
            if status_code == 200 and member and "id" in member:
                member_uuid = member["id"]
                
                # Ahora actualizar el idioma usando el UUID del miembro
                status_code, response = MemberService.update_member(
                    member_uuid,  # UUID del miembro
                    {"language": api_language_code},  # Datos a actualizar
                    token=user_id  # Pasar el telegram_id como token para autorización
                )
                
                if status_code == 200:
                    print(f"Idioma actualizado en la API: {user_id} (UUID: {member_uuid}) -> {api_language_code}")
                else:
                    print(f"Error al actualizar idioma en la API. Status code: {status_code}, Response: {response}")
            else:
                print(f"No se pudo obtener el UUID del miembro con telegram_id {user_id}")
        except Exception as e:
            print(f"Error al actualizar idioma en la API: {str(e)}")
            # Continuamos con el éxito local aunque falle la API
    
    return local_success

def load_language_from_api(user_id: str) -> str:
    """
    Carga el idioma preferido del usuario desde la API y lo establece localmente.
    
    Args:
        user_id: ID del usuario en Telegram.
        
    Returns:
        Código de idioma cargado (en minúsculas: es, en, fr).
    """
    try:
        # Importar aquí para evitar dependencias circulares
        from services.member_service import MemberService
        
        # Obtener información del miembro
        status_code, member = MemberService.get_member(user_id)
        
        if status_code == 200 and member and "language" in member:
            # Convertir el código de idioma de la API al formato del bot (minúsculas)
            api_language = member["language"]
            bot_language = API_TO_BOT_LANGUAGE.get(api_language, DEFAULT_LANGUAGE)
            
            # Establecer localmente
            translator.set_user_language(user_id, bot_language)
            print(f"Idioma cargado desde la API: {user_id} -> {bot_language}")
            
            return bot_language
    except Exception as e:
        print(f"Error al cargar idioma desde la API: {str(e)}")
    
    # Si hay algún error, devolver el idioma por defecto
    return DEFAULT_LANGUAGE

def get_supported_languages() -> Dict[str, str]:
    """
    Obtiene la lista de idiomas soportados.
    
    Returns:
        Diccionario con los códigos de idioma como claves y los nombres como valores.
    """
    return SUPPORTED_LANGUAGES.copy() 