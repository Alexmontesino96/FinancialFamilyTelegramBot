"""
Translator Module

Este módulo proporciona la clase principal para manejar traducciones en la aplicación.
"""

import os
import importlib.util
import logging

logger = logging.getLogger(__name__)

class Translator:
    """
    Clase que maneja las traducciones de mensajes a diferentes idiomas.
    
    Esta clase carga dinámicamente los archivos de mensajes de cada idioma
    y proporciona métodos para obtener mensajes traducidos.
    """
    
    def __init__(self):
        """
        Inicializa el traductor cargando los idiomas disponibles.
        """
        self.languages = {
            'es': self._load_language('es'),
            'en': self._load_language('en'),
            'fr': self._load_language('fr')
        }
        self.default_language = 'es'
        
        # Informar de los idiomas cargados
        logger.info(f"Traductor inicializado con {len(self.languages)} idiomas: {', '.join(self.languages.keys())}")
    
    def get_message(self, key, language=None):
        """
        Obtiene un mensaje traducido al idioma especificado.
        
        Args:
            key (str): Clave del mensaje a traducir
            language (str, opcional): Código del idioma (es, en, fr)
            
        Returns:
            str: Mensaje traducido o la clave si no se encuentra
        """
        # Usar idioma predeterminado si no se especifica
        language = language or self.default_language
        
        # Si el idioma no existe, usar el predeterminado
        if language not in self.languages:
            logger.warning(f"Idioma '{language}' no encontrado, usando '{self.default_language}'")
            language = self.default_language
        
        # Intentar obtener la traducción
        messages = self.languages[language]
        
        # Si la clave no existe en el idioma, intentar en el predeterminado
        if key not in messages:
            logger.warning(f"Clave '{key}' no encontrada en idioma '{language}', buscando en '{self.default_language}'")
            messages = self.languages[self.default_language]
            
            # Si tampoco existe en el idioma predeterminado, devolver la clave
            if key not in messages:
                logger.error(f"Clave '{key}' no encontrada en ningún idioma")
                return f"Missing: {key}"
        
        return messages.get(key)
    
    def _load_language(self, lang_code):
        """
        Carga los mensajes de un idioma específico.
        
        Args:
            lang_code (str): Código del idioma (es, en, fr)
            
        Returns:
            dict: Diccionario con las traducciones o diccionario vacío si no se encuentra
        """
        try:
            # Importar dinámicamente el módulo de mensajes
            module_path = os.path.join(os.path.dirname(__file__), lang_code, 'messages.py')
            
            # Verificar si el archivo existe
            if not os.path.exists(module_path):
                logger.error(f"Archivo de mensajes para idioma '{lang_code}' no encontrado en: {module_path}")
                return {}
            
            # Cargar el módulo
            spec = importlib.util.spec_from_file_location(f"languages.{lang_code}.messages", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extraer las traducciones del módulo
            if hasattr(module, 'Messages'):
                # Filtrar solo los atributos que son constantes (mayúsculas)
                messages = {attr: getattr(module.Messages, attr) 
                           for attr in dir(module.Messages) 
                           if not attr.startswith('_') and attr.isupper()}
                
                logger.info(f"Idioma '{lang_code}' cargado con {len(messages)} mensajes")
                return messages
            else:
                logger.error(f"No se encontró la clase Messages en el módulo de idioma '{lang_code}'")
                return {}
                
        except Exception as e:
            logger.exception(f"Error al cargar el idioma '{lang_code}': {str(e)}")
            return {} 