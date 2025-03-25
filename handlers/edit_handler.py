"""
Edit Handler Module

This module handles all edit and delete operations in the bot, including
editing expense amounts, deleting expenses, deleting payments, and
managing the edit/delete conversation flow.
"""

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from ui.keyboards import Keyboards
from ui.messages import Messages
from ui.formatters import Formatters
from services.expense_service import ExpenseService
from services.payment_service import PaymentService
from services.member_service import MemberService
from services.family_service import FamilyService
from utils.context_manager import ContextManager
from utils.helpers import send_error, notify_unknown_username
from config import EDIT_OPTION, SELECT_EXPENSE, SELECT_PAYMENT, CONFIRM_DELETE, EDIT_EXPENSE_AMOUNT
import traceback

# Conversation states are now imported from config.py

async def show_edit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows options for editing or deleting expenses and payments.
    
    This function verifies the user is in a family and presents options
    for editing or deleting expenses and payments.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Verify the user is in a family
        family_id = context.user_data.get("family_id")
        telegram_id = str(update.effective_user.id)
        
        # If there's no family_id in the context, try to get it
        if not family_id:
            print(f"No hay family_id en el contexto, intentando obtenerlo para el usuario {telegram_id}")
            is_in_family = await ContextManager.check_user_in_family(context, telegram_id)
            
            if not is_in_family:
                # If the user is not in a family, show error message
                await update.message.reply_text(
                    Messages.ERROR_NOT_IN_FAMILY,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            family_id = context.user_data.get("family_id")
            print(f"Family ID obtenido y guardado en el contexto: {family_id}")
        
        # Clear previous edit data
        if "edit_data" in context.user_data:
            del context.user_data["edit_data"]
        
        # Initialize edit data in the context
        context.user_data["edit_data"] = {}
        
        # Show edit options to the user
        await update.message.reply_text(
            Messages.EDIT_OPTIONS,
            reply_markup=Keyboards.get_edit_options_keyboard()
        )
        
        # Move to the next state: select edit option
        return EDIT_OPTION
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Error en show_edit_options: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al mostrar opciones de edición: {str(e)}")
        return ConversationHandler.END

async def handle_edit_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selected edit option.
    
    This function processes the user's selection of what they want to edit
    or delete (expenses or payments) and routes to the appropriate handler.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Get the selected option
        option = update.message.text
        
        # Save the option in the context
        context.user_data["edit_data"]["option"] = option
        
        # Get the family ID and Telegram ID
        family_id = context.user_data.get("family_id")
        telegram_id = str(update.effective_user.id)
        
        # Handle different edit options
        if option == "📝 Editar Gastos":
            # Get all expenses for the family
            status_code, expenses = ExpenseService.get_family_expenses(family_id, telegram_id)
            
            if status_code != 200 or not expenses:
                # If there are no expenses or there was an error, show message
                await update.message.reply_text(
                    Messages.NO_EXPENSES_TO_EDIT,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            # Sort expenses by date (most recent first)
            expenses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Save expenses in the context
            context.user_data["edit_data"]["expenses"] = expenses
            
            # Create keyboard with expense options
            expense_buttons = []
            for expense in expenses[:10]:  # Limit to 10 most recent expenses
                description = expense.get("description", "Sin descripción")
                amount = expense.get("amount", 0)
                expense_id = expense.get("id")
                
                # Format the button text
                button_text = f"{description} - ${amount:.2f}"
                expense_buttons.append([button_text])
                
                # Save the mapping of button text to expense ID
                if "expense_buttons" not in context.user_data["edit_data"]:
                    context.user_data["edit_data"]["expense_buttons"] = {}
                context.user_data["edit_data"]["expense_buttons"][button_text] = expense_id
            
            # Add cancel button
            expense_buttons.append(["❌ Cancelar"])
            
            # Show expense selection message
            await update.message.reply_text(
                Messages.SELECT_EXPENSE_TO_EDIT,
                reply_markup=ReplyKeyboardMarkup(
                    expense_buttons,
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            
            # Move to the next state: select expense
            return SELECT_EXPENSE
            
        elif option == "🗑️ Eliminar Gastos":
            # Get all expenses for the family
            status_code, expenses = ExpenseService.get_family_expenses(family_id, telegram_id)
            
            if status_code != 200 or not expenses:
                # If there are no expenses or there was an error, show message
                await update.message.reply_text(
                    Messages.NO_EXPENSES_TO_DELETE,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            # Sort expenses by date (most recent first)
            expenses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Save expenses in the context
            context.user_data["edit_data"]["expenses"] = expenses
            
            # Create keyboard with expense options
            expense_buttons = []
            for expense in expenses[:10]:  # Limit to 10 most recent expenses
                description = expense.get("description", "Sin descripción")
                amount = expense.get("amount", 0)
                expense_id = expense.get("id")
                
                # Format the button text
                button_text = f"{description} - ${amount:.2f}"
                expense_buttons.append([button_text])
                
                # Save the mapping of button text to expense ID
                if "expense_buttons" not in context.user_data["edit_data"]:
                    context.user_data["edit_data"]["expense_buttons"] = {}
                context.user_data["edit_data"]["expense_buttons"][button_text] = expense_id
            
            # Add cancel button
            expense_buttons.append(["❌ Cancelar"])
            
            # Show expense selection message
            await update.message.reply_text(
                Messages.SELECT_EXPENSE_TO_DELETE,
                reply_markup=ReplyKeyboardMarkup(
                    expense_buttons,
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            
            # Move to the next state: select expense
            return SELECT_EXPENSE
            
        elif option == "🗑️ Eliminar Pagos":
            # Get all payments for the family
            status_code, payments = PaymentService.get_family_payments(family_id, telegram_id)
            
            if status_code != 200 or not payments:
                # If there are no payments or there was an error, show message
                await update.message.reply_text(
                    Messages.NO_PAYMENTS_TO_DELETE,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            # Sort payments by date (most recent first)
            payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Save payments in the context
            context.user_data["edit_data"]["payments"] = payments
            
            # Create keyboard with payment options
            payment_buttons = []
            for payment in payments[:10]:  # Limit to 10 most recent payments
                from_member_name = payment.get("from_member_name", "Desconocido")
                to_member_name = payment.get("to_member_name", "Desconocido")
                amount = payment.get("amount", 0)
                payment_id = payment.get("id")
                
                # Notificar al desarrollador si algún nombre es desconocido
                if from_member_name == "Desconocido":
                    await notify_unknown_username(
                        update, 
                        context, 
                        payment.get("from_member", {}).get("id", "ID no disponible"), 
                        f"edit_handler.py - handle_edit_option - payment list (from_member)"
                    )
                
                if to_member_name == "Desconocido":
                    await notify_unknown_username(
                        update, 
                        context, 
                        payment.get("to_member", {}).get("id", "ID no disponible"), 
                        f"edit_handler.py - handle_edit_option - payment list (to_member)"
                    )
                
                # Format the button text
                button_text = f"{from_member_name} → {to_member_name} - ${amount:.2f}"
                payment_buttons.append([button_text])
                
                # Save the mapping of button text to payment ID
                if "payment_buttons" not in context.user_data["edit_data"]:
                    context.user_data["edit_data"]["payment_buttons"] = {}
                context.user_data["edit_data"]["payment_buttons"][button_text] = payment_id
            
            # Add cancel button
            payment_buttons.append(["❌ Cancelar"])
            
            # Show payment selection message
            await update.message.reply_text(
                Messages.SELECT_PAYMENT_TO_DELETE,
                reply_markup=ReplyKeyboardMarkup(
                    payment_buttons,
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            
            # Move to the next state: select payment
            return SELECT_PAYMENT
            
        elif option == "📝 Editar Pagos":
            # Mostrar mensaje de que esta funcionalidad no está disponible aún
            await update.message.reply_text(
                "La funcionalidad de editar pagos no está disponible en esta versión. Próximamente estará disponible.",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
            
        elif option == "↩️ Volver al Menú":
            # Mostrar el menú principal
            from handlers.menu_handler import show_main_menu
            return await show_main_menu(update, context)
            
        else:
            # If the option is not recognized, show error message
            await update.message.reply_text(
                Messages.INVALID_EDIT_OPTION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
            
    except Exception as e:
        # Handle unexpected errors
        print(f"Error en handle_edit_option: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al procesar la opción de edición: {str(e)}")
        return ConversationHandler.END

async def handle_select_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selection of an expense to edit or delete.
    
    This function processes the user's selection of which expense they want
    to edit or delete and routes to the appropriate next step.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Get the selected expense button text
        selected_text = update.message.text
        
        # Check if the user wants to cancel
        if selected_text == "❌ Cancelar":
            # Show cancel message and return to main menu
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Get the expense ID from the context using the button text
        expense_buttons = context.user_data["edit_data"].get("expense_buttons", {})
        selected_id = expense_buttons.get(selected_text)
        
        if not selected_id:
            # If the expense ID is not found, show error message
            await update.message.reply_text(
                Messages.EXPENSE_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Save the selected expense ID in the context
        context.user_data["edit_data"]["selected_id"] = selected_id
        
        # Get the selected expense details
        expenses = context.user_data["edit_data"].get("expenses", [])
        selected_expense = None
        for expense in expenses:
            if expense.get("id") == selected_id:
                selected_expense = expense
                break
        
        if not selected_expense:
            # If the expense is not found, show error message
            await update.message.reply_text(
                Messages.EXPENSE_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Save the selected expense in the context
        context.user_data["edit_data"]["selected_expense"] = selected_expense
        
        # Get the option (edit or delete)
        option = context.user_data["edit_data"].get("option")
        
        if option == "📝 Editar Gastos":
            # For editing, ask for the new amount
            await update.message.reply_text(
                Messages.EDIT_EXPENSE_AMOUNT.format(
                    details=f"*Descripción:* {selected_expense.get('description', 'Sin descripción')}\n"
                           f"*Monto actual:* ${selected_expense.get('amount', 0):.2f}"
                ),
                parse_mode="Markdown",
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return EDIT_EXPENSE_AMOUNT
            
        elif option == "🗑️ Eliminar Gastos":
            # For deleting, ask for confirmation
            await update.message.reply_text(
                Messages.CONFIRM_DELETE_EXPENSE.format(
                    details=f"*Descripción:* {selected_expense.get('description', 'Sin descripción')}\n"
                           f"*Monto:* ${selected_expense.get('amount', 0):.2f}"
                ),
                parse_mode="Markdown",
                reply_markup=Keyboards.get_confirmation_keyboard()
            )
            return CONFIRM_DELETE
            
        else:
            # If the option is not recognized, show error message
            await update.message.reply_text(
                Messages.INVALID_EDIT_OPTION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
            
    except Exception as e:
        # Handle unexpected errors
        print(f"Error en handle_select_expense: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al seleccionar el gasto: {str(e)}")
        return ConversationHandler.END

async def handle_edit_expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the input of a new amount for an expense.
    
    This function validates and processes the new amount entered by the user
    for editing an expense, then updates the expense in the database.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Get the new amount text
        new_amount_text = update.message.text
        
        # Check if the user canceled the operation
        if new_amount_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.OPERATION_CANCELED,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Try to convert the text to a float
        try:
            # Replace commas with dots for different number formats
            new_amount_text = new_amount_text.replace(',', '.').strip()
            new_amount = float(new_amount_text)
            
            # Verify the amount is positive
            if new_amount <= 0:
                await update.message.reply_text(
                    Messages.INVALID_AMOUNT,
                    reply_markup=Keyboards.get_cancel_keyboard()
                )
                return EDIT_EXPENSE_AMOUNT
                
        except ValueError:
            # If the text cannot be converted to a number, show error message
            await update.message.reply_text(
                Messages.INVALID_AMOUNT,
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return EDIT_EXPENSE_AMOUNT
        
        # Get the expense ID and Telegram ID
        expense_id = context.user_data["edit_data"].get("selected_id")
        telegram_id = str(update.effective_user.id)
        
        if not expense_id:
            # If the expense ID is not found, show error message
            await update.message.reply_text(
                Messages.EXPENSE_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Update the expense with the new amount
        data = {"amount": new_amount}
        status_code, response = ExpenseService.update_expense(expense_id, data, telegram_id)
        
        if status_code in [200, 201]:
            # If the update was successful, show success message
            await update.message.reply_text(
                Messages.EXPENSE_UPDATED_SUCCESS,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
        else:
            # If there was an error, show error message
            error_message = response.get("error", "Error desconocido")
            await update.message.reply_text(
                f"Error al actualizar el gasto: {error_message}",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
        
        # End the conversation
        return ConversationHandler.END
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Error en handle_edit_expense_amount: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al editar el monto del gasto: {str(e)}")
        return ConversationHandler.END

async def handle_select_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selection of a payment to delete.
    
    This function processes the user's selection of which payment they want
    to delete and routes to the appropriate next step.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Get the selected payment button text
        selected_text = update.message.text
        
        # Check if the user wants to cancel
        if selected_text == "❌ Cancelar":
            # Show cancel message and return to main menu
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Get the payment ID from the context using the button text
        payment_buttons = context.user_data["edit_data"].get("payment_buttons", {})
        selected_id = payment_buttons.get(selected_text)
        
        if not selected_id:
            # If the payment ID is not found, show error message
            await update.message.reply_text(
                Messages.PAYMENT_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Save the selected payment ID in the context
        context.user_data["edit_data"]["selected_id"] = selected_id
        
        # Get the selected payment details
        payments = context.user_data["edit_data"].get("payments", [])
        selected_payment = None
        for payment in payments:
            if payment.get("id") == selected_id:
                selected_payment = payment
                break
        
        if not selected_payment:
            # If the payment is not found, show error message
            await update.message.reply_text(
                Messages.PAYMENT_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Save the selected payment in the context
        context.user_data["edit_data"]["selected_payment"] = selected_payment
        
        # Get the option (delete)
        option = context.user_data["edit_data"].get("option")
        
        if option == "🗑️ Eliminar Pagos":
            # For deleting, ask for confirmation
            # Obtener los IDs de los miembros
            from_member = selected_payment.get("from_member", {})
            to_member = selected_payment.get("to_member", {})
            
            # Obtener el ID del miembro que realiza el pago
            from_id = from_member.get("id") if isinstance(from_member, dict) else from_member
            
            # Obtener el ID del miembro que recibe el pago
            to_id = to_member.get("id") if isinstance(to_member, dict) else to_member
            
            # Cargar los nombres de los miembros si no están en el contexto
            member_names = context.user_data.get("member_names", {})
            if not member_names:
                # Cargar los nombres de los miembros desde la API
                family_id = context.user_data.get("family_id")
                telegram_id = str(update.effective_user.id)
                status_code, family = FamilyService.get_family(family_id, telegram_id)
                if status_code == 200 and family and "members" in family:
                    # Crear un diccionario para mapear IDs a nombres de miembros
                    for member in family.get("members", []):
                        member_id = member.get("id")
                        member_name = member.get("name", f"Usuario {member_id}")
                        # Guardar tanto como string como de forma numérica si corresponde
                        member_names[str(member_id)] = member_name
                        if isinstance(member_id, (int, float)) or (isinstance(member_id, str) and member_id.isdigit()):
                            member_names[int(member_id) if isinstance(member_id, str) else member_id] = member_name
                    
                    # Guardar en el contexto para uso futuro
                    context.user_data["member_names"] = member_names
            
            # Intentar obtener el nombre del miembro que realiza el pago
            from_name = None
            if isinstance(from_member, dict) and "name" in from_member:
                from_name = from_member.get("name")
            elif str(from_id) in member_names:
                from_name = member_names[str(from_id)]
            elif from_id in member_names:
                from_name = member_names[from_id]
            else:
                from_name = selected_payment.get("from_member_name", f"Usuario {from_id}")
            
            # Intentar obtener el nombre del miembro que recibe el pago
            to_name = None
            if isinstance(to_member, dict) and "name" in to_member:
                to_name = to_member.get("name")
            elif str(to_id) in member_names:
                to_name = member_names[str(to_id)]
            elif to_id in member_names:
                to_name = member_names[to_id]
            else:
                to_name = selected_payment.get("to_member_name", f"Usuario {to_id}")
            
            amount = selected_payment.get("amount", 0)
            
            await update.message.reply_text(
                Messages.CONFIRM_DELETE_PAYMENT.format(
                    details=f"*De:* {from_name}\n"
                           f"*Para:* {to_name}\n"
                           f"*Monto:* ${amount:.2f}"
                ),
                parse_mode="Markdown",
                reply_markup=Keyboards.get_confirmation_keyboard()
            )
            return CONFIRM_DELETE
            
        else:
            # If the option is not recognized, show error message
            await update.message.reply_text(
                Messages.INVALID_EDIT_OPTION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
            
    except Exception as e:
        # Handle unexpected errors
        print(f"Error en handle_select_payment: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al seleccionar el pago: {str(e)}")
        return ConversationHandler.END

async def handle_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the confirmation of deleting an expense or payment.
    
    This function processes the user's confirmation and deletes the
    selected expense or payment if confirmed.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Get the confirmation response
        response = update.message.text
        
        # Check if the user confirmed
        if response != "✅ Confirmar":
            # If not confirmed, show cancel message and return to main menu
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Get the selected ID and option
        selected_id = context.user_data["edit_data"].get("selected_id")
        option = context.user_data["edit_data"].get("option")
        
        if not selected_id:
            # If the ID is not found, show error message
            await update.message.reply_text(
                "No se encontró el ID del elemento a eliminar.",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Handle different delete options
        if option == "🗑️ Eliminar Gastos":
            # Delete the expense
            status_code, response = ExpenseService.delete_expense(selected_id)
            
            if status_code in [200, 204]:
                # If the deletion was successful, show success message
                await update.message.reply_text(
                    Messages.SUCCESS_EXPENSE_DELETED,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            else:
                # If there was an error, show error message
                error_message = response.get("error", "Error desconocido")
                await update.message.reply_text(
                    f"Error al eliminar el gasto: {error_message}",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
        elif option == "🗑️ Eliminar Pagos":
            # Delete the payment
            status_code, response = PaymentService.delete_payment(selected_id)
            
            if status_code in [200, 204]:
                # If the deletion was successful, show success message
                await update.message.reply_text(
                    Messages.SUCCESS_PAYMENT_DELETED,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            else:
                # If there was an error, show error message
                error_message = response.get("error", "Error desconocido")
                await update.message.reply_text(
                    f"Error al eliminar el pago: {error_message}",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
        else:
            # If the option is not recognized, show error message
            await update.message.reply_text(
                Messages.INVALID_EDIT_OPTION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            
        # End the conversation
        return ConversationHandler.END
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Error en handle_confirm_delete: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al confirmar la eliminación: {str(e)}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancels the current edit/delete operation.
    
    This function handles the cancellation of the edit/delete flow
    and returns the user to the main menu.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    # Clear edit data from the context
    if "edit_data" in context.user_data:
        del context.user_data["edit_data"]
    
    # Show cancellation message
    await update.message.reply_text(
        Messages.OPERATION_CANCELED,
        reply_markup=Keyboards.get_main_menu_keyboard()
    )
    
    # End the conversation
    return ConversationHandler.END