"""
Set Admin Chat Script

Este script permite configurar el ID del chat de administrador para recibir
notificaciones de errores del bot.
"""

import os
import sys
import argparse
from dotenv import load_dotenv, set_key

def main():
    """
    Función principal que configura el ID del chat de administrador.
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Configurar el ID del chat de administrador para recibir errores del bot.')
    parser.add_argument('chat_id', type=str, help='ID del chat de administrador')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Obtener la ruta del archivo .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    # Verificar si el archivo .env existe
    if not os.path.exists(env_path):
        print(f"Error: No se encontró el archivo .env en {env_path}")
        print("Creando un nuevo archivo .env...")
        with open(env_path, 'w') as f:
            f.write(f"ADMIN_CHAT_ID={args.chat_id}\n")
        print(f"Se ha creado el archivo .env con ADMIN_CHAT_ID={args.chat_id}")
        return
    
    # Configurar el ID del chat de administrador
    try:
        set_key(env_path, 'ADMIN_CHAT_ID', args.chat_id)
        print(f"Se ha configurado ADMIN_CHAT_ID={args.chat_id} en {env_path}")
    except Exception as e:
        print(f"Error al configurar ADMIN_CHAT_ID: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 