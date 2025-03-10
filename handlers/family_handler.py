"""
Family Handler Module

This module handles all family-related operations in the bot, including
displaying family information, showing balances between members, and
generating invitation links for new members to join.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ui.messages import Messages
from ui.formatters import Formatters
from services.family_service import FamilyService
from utils.context_manager import ContextManager
from utils.helpers import send_error, create_qr_code
import traceback

# Eliminamos la importación circular
# from handlers.menu_handler import show_main_menu

async def _show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Helper function to show the main menu without circular imports.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    # Importación local para evitar dependencia circular
    from handlers.menu_handler import show_main_menu
    return await show_main_menu(update, context)

async def show_balances(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows the balance information for all family members.
    
    This function retrieves and displays the current balances between
    all members of the family, showing who owes money to whom.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el ID de la familia del contexto o del usuario
        family_id = ContextManager.get_family_id(context)
        print(f"Obteniendo balances para la familia con ID: {family_id}")
        
        # Verificar que el usuario pertenece a una familia
        if not family_id:
            print("No se encontró el ID de familia en el contexto")
            await update.message.reply_text(Messages.ERROR_NOT_IN_FAMILY)
            return ConversationHandler.END
        
        # Obtener el ID de Telegram del usuario para autenticación
        telegram_id = str(update.effective_user.id)
        
        # Guardar el ID de Telegram en el contexto para uso futuro
        context.user_data["telegram_id"] = telegram_id
        
        # Obtener los balances de la familia desde la API
        print(f"Solicitando balances a la API para la familia {family_id} con telegram_id={telegram_id}")
        status_code, balances = FamilyService.get_family_balances(family_id, telegram_id)
        print(f"Respuesta de get_family_balances: status_code={status_code}, balances={balances}")
        
        # Verificar si hubo un error al obtener los balances
        if status_code >= 400 or not balances:
            # Construir mensaje de error con detalles si están disponibles
            error_msg = f"❌ Error al obtener los balances. Código de error: {status_code}"
            if isinstance(balances, dict) and "detail" in balances:
                error_msg += f"\nDetalle: {balances['detail']}"
            print(f"Error al obtener balances: {error_msg}")
            await update.message.reply_text(error_msg)
            # No mostrar el menú aquí, solo informar del error
            return ConversationHandler.END
        
        # Formatear los balances para mostrarlos al usuario
        formatted_balances = Formatters.format_balances(balances)
        
        # Mostrar los balances al usuario
        await update.message.reply_text(
            Messages.BALANCES_HEADER + formatted_balances,
            parse_mode="Markdown"
        )
        
        # Mostrar el menú principal
        return await _show_menu(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en show_balances: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al mostrar los balances: {str(e)}")
        return ConversationHandler.END

async def mostrar_info_familia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows detailed information about the user's family.
    
    This function retrieves and displays information about the family,
    including its name, creation date, and a list of all members.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el ID de la familia del contexto o del usuario
        family_id = ContextManager.get_family_id(context)
        print(f"Obteniendo información para la familia con ID: {family_id}")
        
        # Verificar que el usuario pertenece a una familia
        if not family_id:
            print("No se encontró el ID de familia en el contexto")
            await update.message.reply_text(Messages.ERROR_NOT_IN_FAMILY)
            return ConversationHandler.END
        
        # Obtener el ID de Telegram del usuario para autenticación
        telegram_id = str(update.effective_user.id)
        
        # Obtener la información de la familia desde la API
        status_code, family = FamilyService.get_family(family_id, telegram_id)
        print(f"Respuesta de get_family: status_code={status_code}, family={family}")
        
        # Verificar si hubo un error al obtener la información
        if status_code >= 400 or not family:
            error_msg = f"❌ Error al obtener la información de la familia. Código de error: {status_code}"
            if isinstance(family, dict) and "detail" in family:
                error_msg += f"\nDetalle: {family['detail']}"
            print(f"Error al obtener información de familia: {error_msg}")
            await update.message.reply_text(error_msg)
            return ConversationHandler.END
        
        # Formatear la información de la familia para mostrarla al usuario
        formatted_info = Formatters.format_family_info(family)
        
        # Mostrar la información al usuario
        await update.message.reply_text(
            formatted_info,
            parse_mode="Markdown"
        )
        
        # Mostrar el menú principal
        return await _show_menu(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en mostrar_info_familia: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al mostrar la información de la familia: {str(e)}")
        return ConversationHandler.END

async def compartir_invitacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generates and shares an invitation link for the family.
    
    This function creates a deep link and QR code that can be used
    by other users to join the family directly.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el ID de la familia del contexto o del usuario
        family_id = ContextManager.get_family_id(context)
        print(f"Generando invitación para la familia con ID: {family_id}")
        
        # Verificar que el usuario pertenece a una familia
        if not family_id:
            print("No se encontró el ID de familia en el contexto")
            await update.message.reply_text(Messages.ERROR_NOT_IN_FAMILY)
            return ConversationHandler.END
        
        # Obtener el nombre del bot para generar el enlace de invitación
        bot_username = (await context.bot.get_me()).username
        
        # Crear el enlace de invitación con el ID de la familia
        invite_link = f"https://t.me/{bot_username}?start=join_{family_id}"
        
        # Generar un código QR con el enlace de invitación
        qr_image = create_qr_code(invite_link)
        
        # Enviar el código QR al usuario
        await update.message.reply_photo(
            photo=qr_image,
            caption=Messages.INVITATION_LINK.format(invite_link=invite_link),
            parse_mode="Markdown"
        )
        
        # Mostrar el menú principal
        return await _show_menu(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en compartir_invitacion: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al generar la invitación: {str(e)}")
        return ConversationHandler.END 