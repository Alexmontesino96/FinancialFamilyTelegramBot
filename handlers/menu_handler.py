"""
Menu Handler Module

This module handles the main menu of the bot and processes user selections
from the menu, routing them to the appropriate handlers.
"""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from config import DESCRIPTION, AMOUNT, CONFIRM, SELECT_TO_MEMBER, PAYMENT_AMOUNT, PAYMENT_CONFIRM, LIST_OPTION
from ui.keyboards import Keyboards
from ui.messages import Messages
from ui.formatters import Formatters
from services.expense_service import ExpenseService
from services.payment_service import PaymentService
from services.family_service import FamilyService
from services.member_service import MemberService
from utils.context_manager import ContextManager
from utils.helpers import send_error
from languages.utils.translator import get_message

# Importaciones de otros manejadores para las diferentes opciones del menú
from handlers.expense_handler import crear_gasto, listar_gastos
from handlers.payment_handler import registrar_pago, listar_pagos
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
        
        # Determinar si estamos tratando con un mensaje normal o un callback_query
        is_callback = update.callback_query is not None
        
        # Si es un callback query, obtenemos el chat_id del mensaje del callback
        if is_callback:
            chat_id = update.callback_query.message.chat_id
            # Enviar un nuevo mensaje en lugar de editar
            await context.bot.send_message(
                chat_id=chat_id,
                text=get_message(telegram_id, "LOADING"),
                reply_markup=Keyboards.remove_keyboard()
            )
        else:
            # Caso normal, es un mensaje directo
            await update.message.reply_text(
                get_message(telegram_id, "LOADING"),
                reply_markup=Keyboards.remove_keyboard()
            )
        
        # Cargar miembros si no están en el contexto
        if not context.user_data.get("member_names"):
            await ContextManager.load_family_members(context, family_id)
            
        # Obtener balances para mostrar resumen
        message_menu = get_message(telegram_id, "MAIN_MENU")
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
                        
                        else:
                            # Formato no reconocido
                            print(f"Formato de balances no reconocido: {balances}")
                            if is_callback:
                                await context.bot.send_message(
                                    chat_id=chat_id,
                                    text=get_message(telegram_id, "ERROR_API"),
                                )
                            else:
                                await update.message.reply_text(
                                    get_message(telegram_id, "ERROR_API"),
                                )
                            return ConversationHandler.END
                    
                    # Crear resumen de balances para mostrar en la parte inferior
                    if debts or credits:
                        # Obtener textos traducidos para el resumen de balance
                        try:
                            balance_summary = get_message(telegram_id, "BALANCE_SUMMARY")
                            you_owe = get_message(telegram_id, "YOU_OWE")
                            owe_to = get_message(telegram_id, "OWE_TO")
                            largest_debt = get_message(telegram_id, "LARGEST_DEBT")
                            no_debt = get_message(telegram_id, "NO_DEBT")
                            owed_to_you = get_message(telegram_id, "OWED_TO_YOU")
                            from_user = get_message(telegram_id, "FROM_USER")
                            largest_credit = get_message(telegram_id, "LARGEST_CREDIT")
                            no_credit = get_message(telegram_id, "NO_CREDIT")
                        except Exception as e:
                            print(f"Error obteniendo mensajes traducidos para balance: {str(e)}")
                            # Usar valores por defecto en caso de error
                            balance_summary = "\n\n📊 *Resumen de tu balance:*\n"
                            you_owe = "💸 *Debes:* ${amount:.2f} en total\n"
                            owe_to = "└ A {name}: ${amount:.2f}\n"
                            largest_debt = "└ Mayor deuda con {name}: ${amount:.2f}\n"
                            no_debt = "💸 *No debes dinero a nadie*\n"
                            owed_to_you = "💰 *Te deben:* ${amount:.2f} en total\n"
                            from_user = "└ {name}: ${amount:.2f}\n"
                            largest_credit = "└ Mayor crédito de {name}: ${amount:.2f}\n"
                            no_credit = "💰 *Nadie te debe dinero*\n"
                        
                        bottom_balance = balance_summary
                        
                        # Mostrar deudas (lo que debo)
                        if debts:
                            total_debt = sum(debt["amount"] for debt in debts)
                            bottom_balance += you_owe.replace("{amount:.2f}", f"{total_debt:.2f}")
                            
                            # Mostrar detalle de la deuda más grande si hay varias
                            if len(debts) == 1:
                                bottom_balance += owe_to.replace("{name}", debts[0]["name"]).replace("{amount:.2f}", f"{debts[0]['amount']:.2f}")
                            elif len(debts) > 1:
                                # Ordenar por monto de mayor a menor
                                debts.sort(key=lambda x: x["amount"], reverse=True)
                                bottom_balance += largest_debt.replace("{name}", debts[0]["name"]).replace("{amount:.2f}", f"{debts[0]['amount']:.2f}")
                        else:
                            bottom_balance += no_debt
                        
                        # Mostrar créditos (lo que me deben)
                        if credits:
                            total_credit = sum(credit["amount"] for credit in credits)
                            bottom_balance += owed_to_you.replace("{amount:.2f}", f"{total_credit:.2f}")
                            
                            # Mostrar detalle del crédito más grande si hay varios
                            if len(credits) == 1:
                                bottom_balance += from_user.replace("{name}", credits[0]["name"]).replace("{amount:.2f}", f"{credits[0]['amount']:.2f}")
                            elif len(credits) > 1:
                                # Ordenar por monto de mayor a menor
                                credits.sort(key=lambda x: x["amount"], reverse=True)
                                bottom_balance += largest_credit.replace("{name}", credits[0]["name"]).replace("{amount:.2f}", f"{credits[0]['amount']:.2f}")
                        else:
                            bottom_balance += no_credit
        
        # Mostrar el mensaje del menú principal con el teclado de opciones y resumen de balance
        if is_callback:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message_menu + bottom_balance,
                reply_markup=Keyboards.get_main_menu_keyboard(telegram_id),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                message_menu + bottom_balance,
                reply_markup=Keyboards.get_main_menu_keyboard(telegram_id),
                parse_mode="Markdown"
            )
        
        # Finalizar la conversación actual para permitir nuevas interacciones
        return ConversationHandler.END
        
    except Exception as e:
        print(f"Error en show_main_menu: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # En caso de error, mostrar solo el menú básico
        try:
            if update.callback_query:
                await context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=get_message(telegram_id, "MAIN_MENU"),
                    reply_markup=Keyboards.get_main_menu_keyboard(telegram_id)
                )
            else:
                await update.message.reply_text(
                    get_message(telegram_id, "MAIN_MENU"),
                    reply_markup=Keyboards.get_main_menu_keyboard(telegram_id)
                )
        except Exception as e2:
            print(f"Error secundario en show_main_menu: {str(e2)}")
            # Intento final - enviar mensaje sin contexto
            telegram_id = str(update.effective_user.id)
            await context.bot.send_message(
                chat_id=telegram_id,
                text=get_message(telegram_id, "MAIN_MENU"),
                reply_markup=Keyboards.get_main_menu_keyboard(telegram_id)
            )
            
        return ConversationHandler.END

async def show_list_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra las opciones para listar registros.
    
    Esta función presenta al usuario un submenú para elegir entre
    listar gastos o listar pagos.
    
    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener ID del usuario para traducciones
        telegram_id = str(update.effective_user.id)
        
        list_records_title = get_message(telegram_id, "LIST_RECORDS_TITLE", "📜 *Listar Registros*\n\n")
        what_records = get_message(telegram_id, "WHAT_RECORDS_TO_VIEW", "¿Qué registros quieres consultar?")
        
        await update.message.reply_text(
            f"{list_records_title}{what_records}",
            reply_markup=Keyboards.get_list_options_keyboard(telegram_id),
            parse_mode="Markdown"
        )
        return LIST_OPTION
    except Exception as e:
        print(f"Error en show_list_options: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Obtener ID del usuario para traducciones
        telegram_id = str(update.effective_user.id)
        error_message = get_message(telegram_id, "ERROR_LISTING_OPTIONS", "Error al mostrar las opciones de listado. Por favor, intenta de nuevo.")
        
        await update.message.reply_text(
            error_message,
            reply_markup=Keyboards.get_main_menu_keyboard(telegram_id)
        )
        return ConversationHandler.END

async def handle_list_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Procesa la selección del usuario en el submenú de listado.
    
    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener ID del usuario para traducciones
        telegram_id = str(update.effective_user.id)
        
        # Obtener la opción seleccionada
        option = update.message.text
        from ui.keyboards import Keyboards  # Importación local para evitar dependencias circulares
        
        # Procesar según la opción
        list_expenses_text = Keyboards.get_text(telegram_id, "LIST_EXPENSES")
        list_payments_text = Keyboards.get_text(telegram_id, "LIST_PAYMENTS")
        back_to_menu_text = Keyboards.get_text(telegram_id, "BACK_TO_MENU")
        
        if option == list_expenses_text:
            from handlers.expense_handler import listar_gastos
            return await listar_gastos(update, context)
        elif option == list_payments_text:
            from handlers.payment_handler import listar_pagos
            return await listar_pagos(update, context)
        elif option == back_to_menu_text:
            await show_main_menu(update, context)
            return ConversationHandler.END
        else:
            invalid_option_text = get_message(telegram_id, "ERROR_INVALID_OPTION", "Opción no válida. Por favor, selecciona una opción del menú:")
            await update.message.reply_text(
                invalid_option_text,
                reply_markup=Keyboards.get_list_options_keyboard(telegram_id)
            )
            return LIST_OPTION
    except Exception as e:
        print(f"Error en handle_list_option: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Obtener ID del usuario para traducciones
        telegram_id = str(update.effective_user.id)
        error_message = get_message(telegram_id, "ERROR_PROCESSING_OPTION", "Error al procesar la opción seleccionada. Por favor, intenta de nuevo.")
        
        await update.message.reply_text(
            error_message,
            reply_markup=Keyboards.get_main_menu_keyboard(telegram_id)
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
    
    # Obtener ID del usuario para traducciones
    telegram_id = str(update.effective_user.id)
    
    # Imprimir la opción para depuración
    print(f"Opción seleccionada: {option}")
    
    # Verificar si ya tenemos el ID de familia en el contexto
    if "family_id" in context.user_data:
        family_id = context.user_data["family_id"]
        print(f"Ya tenemos el family_id en el contexto: {family_id}")
    else:
        # Si no tenemos el ID de familia, verificar que el usuario esté en una familia
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
    
    # Importar Keyboards localmente para evitar dependencias circulares
    from ui.keyboards import Keyboards
    
    # Obtener textos traducidos para cada opción del menú
    create_expense_text = Keyboards.get_text(telegram_id, "CREATE_EXPENSE")
    list_expenses_text = Keyboards.get_text(telegram_id, "LIST_EXPENSES")
    register_payment_text = Keyboards.get_text(telegram_id, "REGISTER_PAYMENT")
    list_payments_text = Keyboards.get_text(telegram_id, "LIST_PAYMENTS")
    list_records_text = Keyboards.get_text(telegram_id, "LIST_RECORDS")
    view_balances_text = Keyboards.get_text(telegram_id, "VIEW_BALANCES")
    family_info_text = Keyboards.get_text(telegram_id, "FAMILY_INFO")
    share_invitation_text = Keyboards.get_text(telegram_id, "SHARE_INVITATION")
    edit_delete_text = Keyboards.get_text(telegram_id, "EDIT_DELETE")
    
    # Procesar la opción seleccionada y redirigir al manejador correspondiente
    if option == create_expense_text:
        # Iniciar el flujo de creación de gastos
        return await crear_gasto(update, context)
    elif option == list_expenses_text:
        # OBSOLETO: Ahora se usa Listar Registros > Listar Gastos
        # Mantenemos por compatibilidad
        return await listar_gastos(update, context)
    elif option == register_payment_text:
        # Iniciar el flujo de registro de pagos
        return await registrar_pago(update, context)
    elif option == list_payments_text:
        # OBSOLETO: Ahora se usa Listar Registros > Listar Pagos
        # Mantenemos por compatibilidad
        return await listar_pagos(update, context)
    elif option == list_records_text:
        # Mostrar el submenú de listar registros
        return await show_list_options(update, context)
    elif option == view_balances_text:
        # Mostrar los balances entre miembros de la familia
        return await show_balances(update, context)
    elif option == family_info_text:
        # Mostrar información de la familia
        return await mostrar_info_familia(update, context)
    elif option == share_invitation_text:
        # Generar y compartir un código de invitación
        return await compartir_invitacion(update, context)
    elif option == edit_delete_text:
        # Mostrar opciones de edición y eliminación
        return await show_edit_options(update, context)
    else:
        # Opción no reconocida, mostrar mensaje de error
        invalid_option_text = get_message(telegram_id, "ERROR_INVALID_OPTION", "Opción no válida. Por favor, selecciona una opción del menú:")
        await update.message.reply_text(
            invalid_option_text,
            reply_markup=Keyboards.get_main_menu_keyboard(telegram_id)
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
    # Obtener ID del usuario para traducciones
    telegram_id = str(update.effective_user.id)
    
    # Mostrar mensaje informativo y el menú principal
    unknown_command_text = get_message(telegram_id, "UNKNOWN_COMMAND")
    
    await update.message.reply_text(
        unknown_command_text,
        reply_markup=Keyboards.get_main_menu_keyboard(telegram_id)
    )
    return ConversationHandler.END 