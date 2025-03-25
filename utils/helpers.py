"""
Helper Functions Module

This module provides utility functions used throughout the application.
It includes functions for error handling, QR code generation, and deep link parsing.
"""

import qrcode
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes

async def send_error(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    """
    Sends an error message to the user.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        message (str): Error message to send
    """
    await update.message.reply_text(f"❌ Error: {message}")

def create_qr_code(data):
    """
    Creates a QR code with the provided data.
    
    This function generates a QR code image from the input data,
    which can be used for sharing invitation links or other information.
    
    Args:
        data (str): Data to encode in the QR code
        
    Returns:
        BytesIO: Object containing the QR code image
    """
    # Crear un objeto QR
    qr = qrcode.QRCode(
        version=1,               # Controla el tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,             # El tamaño de cada "cuadradito" del QR
        border=4,                # El grosor del borde en cuadros
    )

    # Agregar los datos al objeto QR
    qr.add_data(data)
    qr.make(fit=True)

    # Crear la imagen
    img = qr.make_image(fill_color="black", back_color="white")

    bio = BytesIO()
    bio.name = 'codigo_qr.png'  # Nombre "ficticio" para el archivo
    img.save(bio, 'PNG')
    bio.seek(0)

    return bio

def parse_deep_link(args):
    """
    Parses arguments from a deep link.
    
    This function extracts the type and value from deep link arguments,
    which are used for actions like joining a family through a shared link.
    
    Args:
        args (list): List of arguments from the deep link
        
    Returns:
        tuple: (type, value) or (None, None) if not a valid deep link
    """
    if not args:
        return None, None
    
    arg = args[0]
    # Manejar tanto "join_" como "join" sin guión bajo
    if arg.startswith("join_"):
        return "join", arg.replace("join_", "")
    elif arg.startswith("join"):
        return "join", arg.replace("join", "")
    
    return None, None 

async def notify_unknown_username(update: Update, context: ContextTypes.DEFAULT_TYPE, member_id: str, location: str):
    """
    Notifies the developer about an unknown username.
    
    This function sends a notification when a username is unknown (displayed as 'Desconocido'),
    which helps identify issues with user data retrieval in the application.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        member_id (str): ID of the member with unknown username
        location (str): Location in the code where the unknown username was detected
    """
    import os
    import html
    from telegram.constants import ParseMode
    from config import logger
    
    user_id = update.effective_user.id
    username = update.effective_user.username or "sin username"
    
    # Crear el mensaje de notificación
    notification = f"⚠️ Usuario desconocido detectado:\n"
    notification += f"- Member ID: {member_id}\n"
    notification += f"- Ubicación: {location}\n"
    notification += f"- Reportado por: {user_id} (@{username})"
    
    # Registrar en el log
    logger.warning(notification)
    
    # Obtener el chat ID del administrador
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    
    # Si no hay un ADMIN_CHAT_ID configurado, usar el chat actual
    if not admin_chat_id and update and hasattr(update, 'effective_chat'):
        admin_chat_id = str(update.effective_chat.id)
        logger.info(f"No ADMIN_CHAT_ID configured, using current chat: {admin_chat_id}")
    
    # Enviar la notificación al administrador
    if admin_chat_id:
        try:
            # Formatear el mensaje para HTML
            notification_html = (
                f"⚠️ <b>Usuario desconocido detectado</b>\n\n"
                f"<b>Member ID:</b> {html.escape(str(member_id))}\n"
                f"<b>Ubicación:</b> {html.escape(location)}\n"
                f"<b>Reportado por:</b> {user_id} (@{html.escape(username)})\n"
            )
            
            # Enviar el mensaje al administrador
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=notification_html,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send unknown username notification to admin: {e}")
    else:
        # Si no hay chat de administrador, imprimir en la consola
        print(notification)