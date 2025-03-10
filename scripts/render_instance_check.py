"""
Render Instance Check Script

Este script está diseñado específicamente para el entorno de Render.
Verifica si hay múltiples instancias del bot ejecutándose y crea un archivo
de bloqueo para evitar que se inicien múltiples instancias.
"""

import os
import sys
import time
import fcntl
import logging
import atexit
import signal
import psutil

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ruta del archivo de bloqueo
LOCK_FILE = '/tmp/telegram_bot.lock'

# Manejador del archivo de bloqueo
lock_file_handle = None

def release_lock():
    """Libera el archivo de bloqueo al salir."""
    global lock_file_handle
    if lock_file_handle:
        try:
            fcntl.flock(lock_file_handle, fcntl.LOCK_UN)
            lock_file_handle.close()
            logger.info("Archivo de bloqueo liberado")
        except Exception as e:
            logger.error(f"Error al liberar el archivo de bloqueo: {e}")

def acquire_lock():
    """
    Intenta adquirir un bloqueo exclusivo en el archivo de bloqueo.
    
    Returns:
        bool: True si se adquirió el bloqueo, False en caso contrario
    """
    global lock_file_handle
    
    try:
        # Crear el archivo de bloqueo si no existe
        lock_file_handle = open(LOCK_FILE, 'w')
        
        # Intentar adquirir el bloqueo sin esperar (no bloqueante)
        fcntl.flock(lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Si llegamos aquí, hemos adquirido el bloqueo
        logger.info(f"Bloqueo adquirido en {LOCK_FILE}")
        
        # Escribir el PID en el archivo de bloqueo
        lock_file_handle.write(str(os.getpid()))
        lock_file_handle.flush()
        
        # Registrar la función para liberar el bloqueo al salir
        atexit.register(release_lock)
        
        # Registrar manejadores de señales para liberar el bloqueo en caso de terminación
        signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
        signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
        
        return True
        
    except IOError:
        # No se pudo adquirir el bloqueo porque otra instancia ya lo tiene
        if lock_file_handle:
            lock_file_handle.close()
            lock_file_handle = None
        
        # Intentar leer el PID del archivo de bloqueo
        try:
            with open(LOCK_FILE, 'r') as f:
                pid_str = f.read().strip()
                if pid_str and pid_str.isdigit():
                    pid = int(pid_str)
                    # Verificar si el proceso con ese PID existe
                    if not psutil.pid_exists(pid):
                        logger.warning(f"El proceso con PID {pid} ya no existe. Eliminando archivo de bloqueo.")
                        os.remove(LOCK_FILE)
                        # Intentar adquirir el bloqueo nuevamente
                        return acquire_lock()
        except Exception as e:
            logger.error(f"Error al leer el PID del archivo de bloqueo: {e}")
        
        logger.warning(f"No se pudo adquirir el bloqueo en {LOCK_FILE}. Otra instancia del bot ya está en ejecución.")
        return False
    except Exception as e:
        logger.error(f"Error al adquirir el bloqueo: {e}")
        if lock_file_handle:
            lock_file_handle.close()
            lock_file_handle = None
        return False

def check_render_instance():
    """
    Verifica si esta instancia debe continuar ejecutándose en el entorno de Render.
    
    Returns:
        bool: True si esta instancia debe continuar, False si debe detenerse
    """
    # Verificar si estamos en el entorno de Render
    if os.environ.get('RENDER') != 'true':
        logger.info("No estamos en el entorno de Render, omitiendo la verificación de instancias")
        return True
    
    # Verificar si hay instancias del bot ejecutándose
    bot_instances = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Verificar si es un proceso de Python
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                # Verificar si está ejecutando main.py
                if cmdline and any('main.py' in arg for arg in cmdline):
                    # No incluir el proceso actual
                    if proc.info['pid'] != os.getpid():
                        bot_instances.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Si hay otras instancias, intentar terminarlas
    if bot_instances:
        logger.warning(f"Se encontraron {len(bot_instances)} instancias del bot: {bot_instances}")
        for pid in bot_instances:
            try:
                logger.info(f"Intentando terminar el proceso con PID {pid}")
                os.kill(pid, signal.SIGTERM)
                # Esperar un momento para que el proceso termine
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error al terminar el proceso {pid}: {e}")
    
    # Intentar adquirir el bloqueo
    if acquire_lock():
        logger.info("Esta instancia es la única en ejecución o la primera en adquirir el bloqueo")
        return True
    else:
        logger.warning("Ya hay otra instancia del bot en ejecución. Esta instancia se detendrá.")
        return False

if __name__ == "__main__":
    # Verificar instancias
    should_continue = check_render_instance()
    
    # Salir si esta instancia debe detenerse
    if not should_continue:
        sys.exit(0)
    
    logger.info("No se encontraron instancias duplicadas o esta es la instancia principal.")
    
    # Mantener el script en ejecución para demostración
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Script detenido por el usuario") 