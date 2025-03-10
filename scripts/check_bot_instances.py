"""
Bot Instance Checker Script

Este script verifica si hay múltiples instancias del bot ejecutándose
y detiene las instancias adicionales para evitar conflictos.
"""

import os
import sys
import psutil
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_script_path():
    """Obtiene la ruta del script principal del bot."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))

def check_bot_instances():
    """
    Verifica si hay múltiples instancias del bot ejecutándose.
    Detiene las instancias adicionales si es necesario.
    
    Returns:
        bool: True si esta instancia debe continuar, False si debe detenerse
    """
    script_path = get_script_path()
    current_pid = os.getpid()
    bot_instances = []
    
    # Buscar procesos de Python que estén ejecutando main.py
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Verificar si es un proceso de Python
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                # Verificar si está ejecutando main.py
                if cmdline and any(Path(arg).name == 'main.py' for arg in cmdline):
                    bot_instances.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Si hay más de una instancia, mantener solo la más antigua
    if len(bot_instances) > 1:
        logger.warning(f"Se encontraron {len(bot_instances)} instancias del bot: {bot_instances}")
        
        # Ordenar por tiempo de inicio (más antiguo primero)
        bot_instances.sort(key=lambda pid: psutil.Process(pid).create_time())
        
        # Si esta instancia no es la más antigua, debe detenerse
        if current_pid != bot_instances[0]:
            logger.info(f"Esta instancia (PID: {current_pid}) no es la más antigua. Deteniendo...")
            return False
        else:
            logger.info(f"Esta instancia (PID: {current_pid}) es la más antigua. Continuando...")
            
            # Detener las demás instancias
            for pid in bot_instances[1:]:
                try:
                    logger.info(f"Deteniendo instancia con PID: {pid}")
                    process = psutil.Process(pid)
                    process.terminate()
                except Exception as e:
                    logger.error(f"Error al detener instancia {pid}: {e}")
    
    return True

if __name__ == "__main__":
    # Verificar instancias
    should_continue = check_bot_instances()
    
    # Salir si esta instancia debe detenerse
    if not should_continue:
        sys.exit(0)
    
    logger.info("No se encontraron instancias duplicadas o esta es la instancia principal.") 