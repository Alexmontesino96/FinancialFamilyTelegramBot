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
from utils.context_manager import ContextManager
from utils.helpers import send_error
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
        if option == "📝 Editar Gasto":
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
            
        elif option == "🗑️ Eliminar Gasto":
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
            
        elif option == "🗑️ Eliminar Pago":
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
        selected_expense_text = update.message.text
        
        # Check if the user canceled the operation
        if selected_expense_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.OPERATION_CANCELED,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Get the expense ID from the button mapping
        expense_buttons = context.user_data["edit_data"].get("expense_buttons", {})
        expense_id = expense_buttons.get(selected_expense_text)
        
        if not expense_id:
            # If the expense ID is not found, show error message
            await update.message.reply_text(
                Messages.EXPENSE_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Save the selected expense ID in the context
        context.user_data["edit_data"]["selected_id"] = expense_id
        
        # Get the selected option (edit or delete)
        option = context.user_data["edit_data"].get("option")
        
        if option == "📝 Editar Gasto":
            # For editing, ask for the new amount
            await update.message.reply_text(
                Messages.ENTER_NEW_EXPENSE_AMOUNT,
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return EDIT_EXPENSE_AMOUNT
            
        elif option == "🗑️ Eliminar Gasto":
            # For deleting, ask for confirmation
            await update.message.reply_text(
                Messages.CONFIRM_DELETE_EXPENSE.format(expense=selected_expense_text),
                reply_markup=Keyboards.get_confirm_keyboard()
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
    to delete and asks for confirmation.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Get the selected payment button text
        selected_payment_text = update.message.text
        
        # Check if the user canceled the operation
        if selected_payment_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.OPERATION_CANCELED,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Get the payment ID from the button mapping
        payment_buttons = context.user_data["edit_data"].get("payment_buttons", {})
        payment_id = payment_buttons.get(selected_payment_text)
        
        if not payment_id:
            # If the payment ID is not found, show error message
            await update.message.reply_text(
                Messages.PAYMENT_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Save the selected payment ID in the context
        context.user_data["edit_data"]["selected_id"] = payment_id
        
        # Ask for confirmation to delete the payment
        await update.message.reply_text(
            Messages.CONFIRM_DELETE_PAYMENT.format(payment=selected_payment_text),
            reply_markup=Keyboards.get_confirm_keyboard()
        )
        
        # Move to the next state: confirm delete
        return CONFIRM_DELETE
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Error en handle_select_payment: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al seleccionar el pago: {str(e)}")
        return ConversationHandler.END

async def handle_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the confirmation for deleting an expense or payment.
    
    This function processes the user's confirmation response and deletes
    the selected expense or payment if confirmed.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Get the confirmation response
        confirmation = update.message.text
        
        # Check if the user canceled the operation
        if confirmation != "✅ Confirmar":
            await update.message.reply_text(
                Messages.OPERATION_CANCELED,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Get the selected ID and option
        selected_id = context.user_data["edit_data"].get("selected_id")
        option = context.user_data["edit_data"].get("option")
        
        if not selected_id:
            # If the ID is not found, show error message
            await update.message.reply_text(
                Messages.ITEM_NOT_FOUND,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Handle different delete options
        if option == "🗑️ Eliminar Gasto":
            # Delete the expense
            status_code, response = ExpenseService.delete_expense(selected_id)
            
            if status_code in [200, 204]:
                # If the deletion was successful, show success message
                await update.message.reply_text(
                    Messages.EXPENSE_DELETED_SUCCESS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            else:
                # If there was an error, show error message
                error_message = response.get("error", "Error desconocido")
                await update.message.reply_text(
                    f"Error al eliminar el gasto: {error_message}",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
        elif option == "🗑️ Eliminar Pago":
            # Delete the payment
            status_code, response = PaymentService.delete_payment(selected_id)
            
            if status_code in [200, 204]:
                # If the deletion was successful, show success message
                await update.message.reply_text(
                    Messages.PAYMENT_DELETED_SUCCESS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            else:
                # If there was an error, show error message
                error_message = response.get("error", "Error desconocido")
                await update.message.reply_text(
                    f"Error al eliminar el pago: {error_message}",
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