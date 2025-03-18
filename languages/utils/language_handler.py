"""
Manejador de idiomas para Telegram

Este módulo proporciona funciones de ayuda para manejar comandos de selección
de idioma en Telegram.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

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
        # Añadir 2 botones por fila
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
    if update.message:
        await update.message.reply_text(
            get_message(user_id, "LANGUAGE_SELECTION"),
            reply_markup=reply_markup
        )
    else:
        # En caso de callback query
        await update.callback_query.edit_message_text(
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
    
    # Para depuración
    print(f"Recibido callback_data: {callback_data}")
    
    # Cancelar operación
    if callback_data == "lang_cancel":
        await query.edit_message_text(get_message(user_id, "CANCEL_OPERATION"))
        return ConversationHandler.END
    
    # Extraer código de idioma
    lang_code = callback_data.split("_")[1]
    
    # Para depuración
    print(f"Cambiando idioma a: {lang_code}")
    
    # Establecer idioma (local y en la API)
    if set_language(user_id, lang_code):
        # Obtener el nombre del idioma para la confirmación
        language_name = SUPPORTED_LANGUAGES[lang_code]
        
        # Para depuración
        print(f"Idioma establecido correctamente a: {language_name}")
        
        # Enviar mensaje de confirmación en el nuevo idioma
        try:
            await query.edit_message_text(get_message(user_id, "LANGUAGE_UPDATED"))
            print("Mensaje de confirmación enviado correctamente")
        except Exception as e:
            print(f"Error al enviar confirmación: {str(e)}")
            await query.edit_message_text(f"✅ Idioma actualizado a {language_name}")
    else:
        # Si ocurrió un error al establecer el idioma
        print("Error al establecer el idioma")
        await query.edit_message_text(
            "❌ Error al cambiar el idioma. Por favor, inténtalo de nuevo más tarde."
        )
    
    # Enviar directamente un nuevo mensaje con el menú principal
    chat_id = update.callback_query.message.chat_id
    try:
        # Importar Keyboards localmente para evitar la dependencia circular
        from ui.keyboards import Keyboards
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=get_message(user_id, "MAIN_MENU"),
            reply_markup=Keyboards.get_main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error al enviar menú principal: {str(e)}")
    
    return ConversationHandler.END

def get_language_handlers():
    """
    Obtiene los manejadores para la funcionalidad de idiomas.
    
    Returns:
        Lista de manejadores para registrar en el bot.
    """
    # Importar los módulos necesarios localmente para evitar dependencias circulares
    from ui.keyboards import Keyboards
    
    # Handler independiente para el callback
    callback_handler = CallbackQueryHandler(language_selection_handler, pattern=r"^lang_")
    
    # Conversation handler para el flujo completo
    language_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("language", language_command),
            MessageHandler(filters.Regex(f"^{Keyboards.DEFAULT_TEXTS['CHANGE_LANGUAGE']}$"), language_command)
        ],
        states={
            SELECTING_LANGUAGE: [
                callback_handler
            ],
        },
        fallbacks=[],
        name="language_conversation"
    )
    
    return [language_conv_handler, callback_handler] 