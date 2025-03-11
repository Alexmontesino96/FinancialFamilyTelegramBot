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
    try:
        # Verificar si tenemos datos de familia y miembro
        telegram_id = str(update.effective_user.id)
        family_id = context.user_data.get("family_id")
        
        # Si no tenemos el ID de familia, obtenerlo
        if not family_id:
            status_code, member = MemberService.get_member(telegram_id)
            if status_code == 200 and member and member.get("family_id"):
                family_id = member.get("family_id")
                context.user_data["family_id"] = family_id
        
        # Cargar miembros si no están en el contexto
        if not context.user_data.get("member_names"):
            await ContextManager.load_family_members(context, family_id)
            
        # Obtener balances para mostrar resumen
        message_menu = Messages.MAIN_MENU
        bottom_balance = ""
        
        if family_id:
            # Obtener los balances del usuario
            status_code, balances = FamilyService.get_family_balances(family_id, telegram_id)
            
            if status_code == 200 and balances:
                member_names = context.user_data.get("member_names", {})
                
                # Identificar el ID del miembro actual
                member_id = None
                if "family" in context.user_data and "members" in context.user_data["family"]:
                    for member in context.user_data["family"]["members"]:
                        if member.get("telegram_id") == telegram_id:
                            member_id = member.get("id")
                            break
                
                # Si no encontramos el ID de esta manera, buscarlo en la API
                if not member_id and "family_id" in context.user_data:
                    status_code, member = MemberService.get_member(telegram_id)
                    if status_code == 200 and member:
                        member_id = member.get("id")
                
                # Si tenemos el ID del miembro, buscar sus balances
                if member_id:
                    debts = []  # Lista para almacenar deudas (lo que debo)
                    credits = []  # Lista para almacenar créditos (lo que me deben)
                    
                    # Procesar según el formato de balances
                    if isinstance(balances, list) and len(balances) > 0:
                        if "member_id" in balances[0]:
                            # Formato detallado
                            for balance in balances:
                                if str(balance.get("member_id")) == str(member_id):
                                    for debt in balance.get("debts", []):
                                        to_id = debt.get("to")
                                        amount = debt.get("amount", 0)
                                        to_name = member_names.get(str(to_id), f"Usuario {to_id}")
                                        if amount > 0:
                                            debts.append({"name": to_name, "amount": amount})
                                    
                                    for credit in balance.get("credits", []):
                                        from_id = credit.get("from")
                                        amount = credit.get("amount", 0)
                                        from_name = member_names.get(str(from_id), f"Usuario {from_id}")
                                        if amount > 0:
                                            credits.append({"name": from_name, "amount": amount})
                        
                        elif "from_member" in balances[0] and "to_member" in balances[0]:
                            # Formato de transacciones
                            for transaction in balances:
                                if str(transaction.get("from_member")) == str(member_id):
                                    to_id = transaction.get("to_member")
                                    amount = transaction.get("amount", 0)
                                    to_name = member_names.get(str(to_id), f"Usuario {to_id}")
                                    if amount > 0:
                                        debts.append({"name": to_name, "amount": amount})
                                
                                elif str(transaction.get("to_member")) == str(member_id):
                                    from_id = transaction.get("from_member")
                                    amount = transaction.get("amount", 0)
                                    from_name = member_names.get(str(from_id), f"Usuario {from_id}")
                                    if amount > 0:
                                        credits.append({"name": from_name, "amount": amount})
                        
                        else:
                            # Formato antiguo
                            for balance in balances:
                                if isinstance(balance, dict):
                                    if str(balance.get("debtor_id")) == str(member_id):
                                        creditor_id = balance.get("creditor_id")
                                        amount = balance.get("amount", 0)
                                        creditor_name = member_names.get(str(creditor_id), f"Usuario {creditor_id}")
                                        if amount > 0:
                                            debts.append({"name": creditor_name, "amount": amount})
                                    
                                    elif str(balance.get("creditor_id")) == str(member_id):
                                        debtor_id = balance.get("debtor_id")
                                        amount = balance.get("amount", 0)
                                        debtor_name = member_names.get(str(debtor_id), f"Usuario {debtor_id}")
                                        if amount > 0:
                                            credits.append({"name": debtor_name, "amount": amount})
                    
                    # Crear resumen de balances para mostrar en la parte inferior
                    if debts or credits:
                        bottom_balance = "\n\n📊 *Resumen de tu balance:*\n"
                        
                        # Mostrar deudas (lo que debo)
                        if debts:
                            total_debt = sum(debt["amount"] for debt in debts)
                            bottom_balance += f"💸 *Debes:* ${total_debt:.2f} en total\n"
                            
                            # Mostrar detalle de la deuda más grande si hay varias
                            if len(debts) == 1:
                                bottom_balance += f"└ A {debts[0]['name']}: ${debts[0]['amount']:.2f}\n"
                            elif len(debts) > 1:
                                # Ordenar por monto de mayor a menor
                                debts.sort(key=lambda x: x["amount"], reverse=True)
                                bottom_balance += f"└ Mayor deuda con {debts[0]['name']}: ${debts[0]['amount']:.2f}\n"
                        else:
                            bottom_balance += "💸 *No debes dinero a nadie*\n"
                        
                        # Mostrar créditos (lo que me deben)
                        if credits:
                            total_credit = sum(credit["amount"] for credit in credits)
                            bottom_balance += f"💰 *Te deben:* ${total_credit:.2f} en total\n"
                            
                            # Mostrar detalle del crédito más grande si hay varios
                            if len(credits) == 1:
                                bottom_balance += f"└ {credits[0]['name']}: ${credits[0]['amount']:.2f}\n"
                            elif len(credits) > 1:
                                # Ordenar por monto de mayor a menor
                                credits.sort(key=lambda x: x["amount"], reverse=True)
                                bottom_balance += f"└ Mayor crédito de {credits[0]['name']}: ${credits[0]['amount']:.2f}\n"
                        else:
                            bottom_balance += "💰 *Nadie te debe dinero*\n"
        
        # Mostrar el mensaje del menú principal con el teclado de opciones y resumen de balance
        await update.message.reply_text(
            message_menu + bottom_balance,
            reply_markup=Keyboards.get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
        
        # Finalizar la conversación actual para permitir nuevas interacciones
        return ConversationHandler.END
        
    except Exception as e:
        print(f"Error en show_main_menu: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # En caso de error, mostrar solo el menú básico
        await update.message.reply_text(
            Messages.MAIN_MENU,
            reply_markup=Keyboards.get_main_menu_keyboard()
        )
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