"""
Menu Handler Module

This module handles the main menu of the bot and processes user selections
from the menu, routing them to the appropriate handlers.
"""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from config import DESCRIPTION, AMOUNT, CONFIRM, SELECT_TO_MEMBER, PAYMENT_AMOUNT, PAYMENT_CONFIRM
from ui.keyboards import Keyboards
from ui.messages import Messages
from ui.formatters import Formatters
from services.expense_service import ExpenseService
from services.payment_service import PaymentService
from services.family_service import FamilyService
from services.member_service import MemberService
from utils.context_manager import ContextManager
from utils.helpers import send_error

# Importaciones de otros manejadores para las diferentes opciones del menú
from handlers.expense_handler import crear_gasto, listar_gastos
from handlers.payment_handler import registrar_pago
from handlers.family_handler import show_balances, mostrar_info_familia, compartir_invitacion
from handlers.edit_handler import show_edit_options

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows the main menu for users in a family.
    
    This function displays the main menu with options for managing expenses,
    payments, viewing balances, and other family-related actions.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    # Mostrar el mensaje del menú principal con el teclado de opciones
    await update.message.reply_text(
        Messages.MAIN_MENU,
        reply_markup=Keyboards.get_main_menu_keyboard()
    )
    # Finalizar la conversación actual para permitir nuevas interacciones
    return ConversationHandler.END

async def handle_menu_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the main menu options selected by the user.
    
    This function processes the user's selection from the main menu and
    routes to the appropriate handler based on the option chosen.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    # Obtener la opción seleccionada por el usuario
    option = update.message.text
    
    # Imprimir la opción para depuración
    print(f"Opción seleccionada: {option}")
    
    # Verificar si ya tenemos el ID de familia en el contexto
    if "family_id" in context.user_data:
        family_id = context.user_data["family_id"]
        print(f"Ya tenemos el family_id en el contexto: {family_id}")
    else:
        # Si no tenemos el ID de familia, verificar que el usuario esté en una familia
        telegram_id = str(update.effective_user.id)
        print(f"Solicitando información del miembro con telegram_id: {telegram_id}")
        
        # Obtener información del miembro desde la API
        status_code, member = MemberService.get_member(telegram_id)
        
        # Si el usuario no está en una familia, mostrar error y terminar
        if status_code != 200 or not member or not member.get("family_id"):
            await update.message.reply_text(Messages.ERROR_NOT_IN_FAMILY)
            return ConversationHandler.END
        
        # Guardar el ID de familia en el contexto para futuras consultas
        family_id = member.get("family_id")
        context.user_data["family_id"] = family_id
        print(f"Guardando family_id en el contexto: {family_id}")
        
        # También guardar la información de la familia para acceso rápido
        context.user_data["family"] = member.get("family", {})
        
        # Cargar los nombres de los miembros en el contexto para uso futuro
        await ContextManager.load_family_members(context, family_id)
    
    # Procesar la opción seleccionada y redirigir al manejador correspondiente
    if option == "💸 Crear Gasto":
        # Iniciar el flujo de creación de gastos
        return await crear_gasto(update, context)
    elif option == "📋 Ver Gastos":
        # Mostrar la lista de gastos de la familia
        return await listar_gastos(update, context)
    elif option == "💳 Registrar Pago":
        # Iniciar el flujo de registro de pagos
        return await registrar_pago(update, context)
    elif option == "💰 Ver Balances":
        # Mostrar los balances entre miembros de la familia
        return await show_balances(update, context)
    elif option == "ℹ️ Info Familia":
        # Mostrar información de la familia
        return await mostrar_info_familia(update, context)
    elif option == "🔗 Compartir Invitación":
        # Generar y compartir un código de invitación
        return await compartir_invitacion(update, context)
    elif option == "✏️ Editar/Eliminar":
        # Mostrar opciones de edición y eliminación
        return await show_edit_options(update, context)
    else:
        # Opción no reconocida, mostrar mensaje de error
        await update.message.reply_text(
            "Opción no válida. Por favor, selecciona una opción del menú:",
            reply_markup=Keyboards.get_main_menu_keyboard()
        )
        return ConversationHandler.END

async def handle_unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles unknown text messages from the user.
    
    This function is called when the user sends a message that doesn't match
    any of the expected patterns. It shows the main menu as a fallback.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    # Mostrar mensaje informativo y el menú principal
    await update.message.reply_text(
        "No entiendo ese comando. Aquí tienes el menú principal:",
        reply_markup=Keyboards.get_main_menu_keyboard()
    )
    return ConversationHandler.END 