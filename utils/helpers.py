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
    if arg.startswith("join_"):
        return "join", arg.replace("join_", "")
    
    return None, None 