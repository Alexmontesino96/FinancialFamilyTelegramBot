"""
Payment Handler Module

This module handles all payment-related operations in the bot, including
registering payments between family members, confirming payments, and
managing payment data throughout the conversation flow.
"""

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import SELECT_TO_MEMBER, PAYMENT_AMOUNT, PAYMENT_CONFIRM
from ui.keyboards import Keyboards
from ui.messages import Messages
from services.payment_service import PaymentService
from services.family_service import FamilyService
from services.member_service import MemberService
from utils.context_manager import ContextManager
from utils.helpers import send_error

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

async def registrar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the payment registration flow.
    
    This function checks if the user is in a family, retrieves family members,
    and starts the conversation flow for registering a payment to another member.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Limpiar datos previos para evitar conflictos
        if "payment_data" in context.user_data:
            del context.user_data["payment_data"]
        
        # Inicializar estructura de datos para el pago en el contexto
        context.user_data["payment_data"] = {}
        
        # Obtener el ID de Telegram del usuario actual
        telegram_id = str(update.effective_user.id)
        print(f"Buscando miembro con telegram_id: {telegram_id}")
        
        # Verificar si el usuario pertenece a una familia
        status_code, member = MemberService.get_member(telegram_id)
        print(f"Respuesta de get_member: status_code={status_code}, member={member}")
        
        # Si el usuario no está en una familia, mostrar error y terminar
        if status_code != 200 or not member or not member.get("family_id"):
            await update.message.reply_text(
                Messages.ERROR_NOT_IN_FAMILY,
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Obtener el ID de la familia del usuario
        family_id = member.get("family_id")
        print(f"ID de familia obtenido: {family_id}")
        
        # Obtener el ID del miembro que realiza el pago (from_member)
        from_member_id = member.get("id")
        
        # Guardar datos iniciales en el contexto
        context.user_data["payment_data"]["from_member_id"] = from_member_id
        context.user_data["payment_data"]["family_id"] = family_id
        context.user_data["payment_data"]["telegram_id"] = telegram_id
        
        # Obtener todos los miembros de la familia para mostrar opciones de pago
        status_code, family = FamilyService.get_family(family_id, telegram_id)
        
        if status_code != 200 or not family:
            # Si hay error al obtener la familia, mostrar mensaje y terminar
            await update.message.reply_text(
                "Error al obtener los miembros de la familia.",
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Obtener la lista de miembros de la familia
        members = family.get("members", [])
        
        # Filtrar para excluir al usuario actual de la lista de destinatarios
        other_members = [m for m in members if m.get("id") != from_member_id]
        
        if not other_members:
            # Si no hay otros miembros, no se puede registrar un pago
            await update.message.reply_text(
                "No hay otros miembros en la familia a quienes puedas registrar un pago.",
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Guardar la lista de miembros en el contexto para uso posterior
        context.user_data["payment_data"]["members"] = members
        context.user_data["payment_data"]["other_members"] = other_members
        
        # Crear teclado con los nombres de los miembros
        member_buttons = [[member.get("name", "Desconocido")] for member in other_members]
        member_buttons.append(["❌ Cancelar"])
        
        # Mostrar mensaje para seleccionar el destinatario del pago
        await update.message.reply_text(
            Messages.SELECT_PAYMENT_RECIPIENT,
            reply_markup=ReplyKeyboardMarkup(
                member_buttons, 
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        
        # Pasar al siguiente estado: seleccionar destinatario
        return SELECT_TO_MEMBER
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en registrar_pago: {str(e)}")
        await send_error(update, context, f"Error al iniciar el registro de pago: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def select_to_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selection of the payment recipient.
    
    This function processes the user's selection of which family member
    will receive the payment and prompts for the payment amount.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el nombre del miembro seleccionado
        selected_name = update.message.text
        
        # Verificar si el usuario canceló la operación
        if selected_name == "❌ Cancelar":
            await update.message.reply_text(
                "Has cancelado el registro de pago.",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Obtener la lista de otros miembros del contexto
        other_members = context.user_data.get("payment_data", {}).get("other_members", [])
        
        # Buscar el miembro seleccionado por nombre
        to_member = next((m for m in other_members if m.get("name") == selected_name), None)
        
        if not to_member:
            # Si no se encuentra el miembro, mostrar error y volver a pedir
            await update.message.reply_text(
                "Miembro no encontrado. Por favor, selecciona un miembro de la lista:",
                reply_markup=ReplyKeyboardMarkup(
                    [[m.get("name", "Desconocido")] for m in other_members] + [["❌ Cancelar"]],
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            return SELECT_TO_MEMBER
        
        # Guardar el ID del miembro destinatario en el contexto
        to_member_id = to_member.get("id")
        context.user_data["payment_data"]["to_member_id"] = to_member_id
        context.user_data["payment_data"]["to_member_name"] = selected_name
        
        # Pedir el monto del pago
        await update.message.reply_text(
            Messages.CREATE_PAYMENT_AMOUNT.format(to_member=selected_name),
            parse_mode="Markdown",
            reply_markup=Keyboards.get_cancel_keyboard()
        )
        
        # Pasar al siguiente estado: ingresar monto
        return PAYMENT_AMOUNT
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en select_to_member: {str(e)}")
        await send_error(update, context, f"Error al seleccionar el destinatario: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def get_payment_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the payment amount input from the user.
    
    This function validates and saves the payment amount provided by the user,
    then shows a confirmation message with the payment details.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el texto del monto ingresado
        amount_text = update.message.text
        
        # Verificar si el usuario canceló la operación
        if amount_text == "❌ Cancelar":
            await update.message.reply_text(
                "Has cancelado el registro de pago.",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Intentar convertir el texto a un número flotante
        try:
            # Reemplazar comas por puntos para manejar diferentes formatos numéricos
            amount_text = amount_text.replace(',', '.').strip()
            amount = float(amount_text)
            
            # Verificar que el monto sea positivo
            if amount <= 0:
                await update.message.reply_text(
                    "El monto debe ser un número positivo. Por favor, ingresa el monto nuevamente:",
                    reply_markup=Keyboards.get_cancel_keyboard()
                )
                return PAYMENT_AMOUNT
                
        except ValueError:
            # Si no se puede convertir a número, mostrar error
            await update.message.reply_text(
                "El valor ingresado no es un número válido. Por favor, ingresa solo números:",
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return PAYMENT_AMOUNT
            
        # Guardar el monto validado en el contexto
        context.user_data["payment_data"]["amount"] = amount
        
        # Mostrar la confirmación del pago
        return await show_payment_confirmation(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en get_payment_amount: {str(e)}")
        await send_error(update, context, f"Error al procesar el monto del pago: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def show_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows a confirmation message with the payment details.
    
    This function displays the payment information for the user to confirm
    before registering it in the database.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener los datos del pago del contexto
        payment_data = context.user_data.get("payment_data", {})
        to_member_name = payment_data.get("to_member_name", "Desconocido")
        amount = payment_data.get("amount", 0)
        
        # Obtener información sobre el miembro que realiza el pago
        from_member_id = payment_data.get("from_member_id")
        from_member_name = "Tú"  # Por defecto
        
        if "members" in payment_data:
            for member in payment_data.get("members", []):
                if member.get("id") == from_member_id:
                    from_member_name = member.get("name", "Tú")
                    break
        
        # Mostrar mensaje de confirmación con los detalles del pago
        await update.message.reply_text(
            Messages.CREATE_PAYMENT_CONFIRM.format(
                from_member=from_member_name,
                to_member=to_member_name,
                amount=amount
            ),
            parse_mode="Markdown",
            reply_markup=Keyboards.get_confirmation_keyboard()
        )
        
        # Pasar al siguiente estado: confirmar pago
        return PAYMENT_CONFIRM
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en show_payment_confirmation: {str(e)}")
        await send_error(update, context, f"Error al mostrar la confirmación del pago: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's confirmation response for creating a payment.
    
    This function processes the user's confirmation and creates the payment
    in the database if confirmed, or cancels the operation if rejected.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener la respuesta del usuario (confirmar o cancelar)
        response = update.message.text.strip()
        
        # Obtener los datos del pago desde el contexto
        payment_data = context.user_data.get("payment_data", {})
        
        # Verificar acciones específicas
        if response == "✅ Confirmar":
            # Si el usuario confirma, obtener datos necesarios para crear el pago
            amount = payment_data.get("amount")
            from_member_id = payment_data.get("from_member_id")
            to_member_id = payment_data.get("to_member_id")
            telegram_id = payment_data.get("telegram_id")
            family_id = payment_data.get("family_id")
            
            # Validar que todos los datos requeridos estén presentes
            if not all([from_member_id, to_member_id, amount]):
                # Si falta algún dato, mostrar error
                await update.message.reply_text(
                    "Faltan datos para crear el pago. Por favor, inténtalo de nuevo.",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return await _show_menu(update, context)
            
            # Crear el pago a través del servicio
            status_code, response_data = PaymentService.create_payment(
                family_id=family_id,
                amount=amount,
                from_member=from_member_id,
                to_member=to_member_id,
                telegram_id=telegram_id
            )
            
            if status_code in [200, 201]:
                # Si el pago se creó exitosamente, mostrar mensaje de éxito
                await update.message.reply_text(
                    Messages.SUCCESS_PAYMENT_CREATED,
                    parse_mode="Markdown",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
                # Limpiar los datos del pago del contexto
                if "payment_data" in context.user_data:
                    del context.user_data["payment_data"]
                
                # Volver al menú principal
                return await _show_menu(update, context)
            else:
                # Si hubo un error al crear el pago, mostrar mensaje de error
                error_message = response_data.get("error", "Error desconocido")
                await send_error(update, context, f"Error al registrar el pago: {error_message}")
                return await _show_menu(update, context)
        elif response == "❌ Cancelar":
            # Si el usuario cancela, mostrar mensaje y volver al menú principal
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            
            # Limpiar los datos del pago del contexto
            if "payment_data" in context.user_data:
                del context.user_data["payment_data"]
            
            # Volver al menú principal
            return await _show_menu(update, context)
        else:
            # Si la respuesta no es reconocida
            await update.message.reply_text(
                "Opción no reconocida. Por favor, selecciona Confirmar o Cancelar.",
                reply_markup=Keyboards.get_confirmation_keyboard()
            )
            return PAYMENT_CONFIRM
            
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en confirm_payment: {str(e)}")
        await send_error(update, context, f"Error al confirmar el pago: {str(e)}")
        return await _show_menu(update, context) 