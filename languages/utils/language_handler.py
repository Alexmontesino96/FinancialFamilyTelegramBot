"""
Manejador de idiomas para Telegram

Este módulo proporciona funciones de ayuda para manejar comandos de selección
de idioma en Telegram.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler

from languages.utils.translator import SUPPORTED_LANGUAGES, set_language, get_message

# Estados para el conversation handler
SELECTING_LANGUAGE = 1

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Comando para cambiar el idioma del usuario.
    
    Args:
        update: Objeto de actualización de Telegram.
        context: Contexto del bot.
        
    Returns:
        Estado de la conversación.
    """
    # Crear teclado con opciones de idioma
    keyboard = []
    row = []
    for code, name in SUPPORTED_LANGUAGES.items():
        # Añadir 3 botones por fila
        if len(row) < 2:
            row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        else:
            row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
            keyboard.append(row)
            row = []
    
    # Añadir la última fila si quedaron botones
    if row:
        keyboard.append(row)
    
    # Añadir botón de cancelar
    keyboard.append([InlineKeyboardButton("❌ Cancel/Cancelar", callback_data="lang_cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Obtener ID del usuario
    user_id = str(update.effective_user.id)
    
    # Enviar mensaje de selección de idioma
    await update.message.reply_text(
        get_message(user_id, "LANGUAGE_SELECTION"),
        reply_markup=reply_markup
    )
    
    return SELECTING_LANGUAGE

async def language_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Maneja la selección de idioma.
    
    Args:
        update: Objeto de actualización de Telegram.
        context: Contexto del bot.
        
    Returns:
        Estado final de la conversación.
    """
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = str(update.effective_user.id)
    
    # Cancelar operación
    if callback_data == "lang_cancel":
        await query.edit_message_text(get_message(user_id, "CANCEL_OPERATION"))
        return ConversationHandler.END
    
    # Extraer código de idioma
    lang_code = callback_data.split("_")[1]
    
    # Establecer idioma
    if set_language(user_id, lang_code):
        # Obtener el nombre del idioma para la confirmación
        language_name = SUPPORTED_LANGUAGES[lang_code]
        
        # Enviar mensaje de confirmación en el nuevo idioma
        await query.edit_message_text(get_message(user_id, "LANGUAGE_UPDATED"))
    else:
        # Si ocurrió un error al establecer el idioma
        await query.edit_message_text(
            "❌ Error al cambiar el idioma. Por favor, inténtalo de nuevo más tarde."
        )
    
    return ConversationHandler.END

def get_language_handlers():
    """
    Obtiene los manejadores para la funcionalidad de idiomas.
    
    Returns:
        Lista de manejadores para registrar en el bot.
    """
    language_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("language", language_command)],
        states={
            SELECTING_LANGUAGE: [
                CallbackQueryHandler(language_selection_handler, pattern=r"^lang_")
            ],
        },
        fallbacks=[]
    )
    
    return [language_conv_handler] 