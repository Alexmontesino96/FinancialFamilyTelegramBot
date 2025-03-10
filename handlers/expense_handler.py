"""
Expense Handler Module

This module handles all expense-related operations in the bot, including
creating new expenses, listing existing expenses, and managing expense data.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import DESCRIPTION, AMOUNT, CONFIRM
from ui.keyboards import Keyboards
from ui.messages import Messages
from ui.formatters import Formatters
from services.expense_service import ExpenseService
from utils.context_manager import ContextManager
from utils.helpers import send_error
from services.member_service import MemberService
from services.family_service import FamilyService
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

async def crear_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the expense creation flow.
    
    This function checks if the user is in a family and starts the
    conversation flow for creating a new expense.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Verificar que el usuario está en una familia usando su ID de Telegram
        telegram_id = str(update.effective_user.id)
        status_code, member = MemberService.get_member(telegram_id)
        
        # Si el usuario no está en una familia, mostrar error y terminar la conversación
        if status_code != 200 or not member or not member.get("family_id"):
            await update.message.reply_text(
                Messages.ERROR_NOT_IN_FAMILY,
                reply_markup=Keyboards.remove_keyboard()
            )
            return ConversationHandler.END
        
        # Inicializar los datos del gasto en el contexto del usuario
        # Esto permitirá acumular la información a lo largo de la conversación
        context.user_data["expense_data"] = {
            "telegram_id": telegram_id,
            "member_id": member.get("id"),
            "family_id": member.get("family_id")
        }
        
        # Mostrar mensaje introductorio y pedir la descripción del gasto
        await update.message.reply_text(
            Messages.CREATE_EXPENSE_INTRO,
            parse_mode="Markdown",
            reply_markup=Keyboards.get_cancel_keyboard()
        )
        # Pasar al siguiente estado: pedir descripción
        return DESCRIPTION
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en crear_gasto: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al iniciar la creación del gasto.")
        return ConversationHandler.END

async def get_expense_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the expense description input from the user.
    
    This function saves the description provided by the user and
    prompts for the expense amount.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener y validar la descripción del gasto
        description = update.message.text.strip()
        
        # Verificar si el usuario quiere cancelar la operación
        if description == "❌ Cancelar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            # Limpiar datos temporales
            if "expense_data" in context.user_data:
                del context.user_data["expense_data"]
            return await _show_menu(update, context)
        
        # Verificar que la descripción no esté vacía
        if not description:
            await update.message.reply_text(
                "La descripción no puede estar vacía. Por favor, ingresa una descripción para el gasto:",
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            # Permanecer en el mismo estado para pedir nuevamente la descripción
            return DESCRIPTION
            
        # Guardar la descripción en el contexto del usuario
        context.user_data["expense_data"]["description"] = description
        
        # Pedir el monto del gasto
        await update.message.reply_text(
            Messages.CREATE_EXPENSE_AMOUNT.format(description=description),
            parse_mode="Markdown",
            reply_markup=Keyboards.get_cancel_keyboard()
        )
        # Pasar al siguiente estado: pedir monto
        return AMOUNT
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en get_expense_description: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al procesar la descripción del gasto.")
        return ConversationHandler.END

async def get_expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the expense amount input from the user.
    
    This function validates and saves the amount provided by the user,
    then shows a confirmation message with the expense details.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el texto del monto ingresado por el usuario
        amount_text = update.message.text.strip()
        
        # Verificar si el usuario quiere cancelar la operación
        if amount_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            # Limpiar datos temporales
            if "expense_data" in context.user_data:
                del context.user_data["expense_data"]
            return await _show_menu(update, context)
        
        # Intentar convertir el texto a un número flotante
        try:
            # Reemplazar comas por puntos para manejar diferentes formatos numéricos
            amount_text = amount_text.replace(',', '.')
            amount = float(amount_text)
            
            # Verificar que el monto sea positivo
            if amount <= 0:
                await update.message.reply_text(
                    "El monto debe ser un número positivo. Por favor, ingresa el monto nuevamente:",
                    reply_markup=Keyboards.get_cancel_keyboard()
                )
                # Permanecer en el mismo estado para pedir nuevamente el monto
                return AMOUNT
                
        except ValueError:
            # Si no se puede convertir a número, mostrar error
            await update.message.reply_text(
                "El valor ingresado no es un número válido. Por favor, ingresa solo números:",
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            # Permanecer en el mismo estado para pedir nuevamente el monto
            return AMOUNT
            
        # Guardar el monto validado en el contexto del usuario
        context.user_data["expense_data"]["amount"] = amount
        
        # Mostrar la confirmación del gasto
        return await show_expense_confirmation(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en get_expense_amount: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al procesar el monto del gasto.")
        return ConversationHandler.END

async def show_expense_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows a confirmation message with the expense details.
    
    This function displays the expense information for the user to confirm
    before creating it in the database.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    # Obtener los datos del gasto del contexto del usuario
    expense_data = context.user_data.get("expense_data", {})
    description = expense_data.get("description", "")
    amount = expense_data.get("amount", 0)
    
    # Mostrar mensaje de confirmación con los detalles del gasto
    await update.message.reply_text(
        Messages.CREATE_EXPENSE_CONFIRM.format(
            description=description,
            amount=amount,
            paid_by="Tú"
        ),
        parse_mode="Markdown",
        reply_markup=Keyboards.get_confirmation_keyboard()
    )
    # Pasar al siguiente estado: confirmar gasto
    return CONFIRM

async def confirm_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's confirmation response for creating an expense.
    
    This function processes the user's confirmation and creates the expense
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
        
        if response == "✅ Confirmar":
            # Si el usuario confirma, obtener los datos del gasto
            expense_data = context.user_data.get("expense_data", {})
            description = expense_data.get("description", "")
            amount = expense_data.get("amount", 0)
            member_id = expense_data.get("member_id")
            telegram_id = expense_data.get("telegram_id")
            
            # Crear el gasto en la base de datos a través del servicio
            status_code, response_data = ExpenseService.create_expense(
                description=description,
                amount=amount,
                paid_by=member_id,
                telegram_id=telegram_id
            )
            
            if status_code in [200, 201]:
                # Si la creación fue exitosa, mostrar mensaje de éxito
                await update.message.reply_text(
                    Messages.SUCCESS_EXPENSE_CREATED,
                    parse_mode="Markdown",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
                # Limpiar los datos del gasto del contexto
                if "expense_data" in context.user_data:
                    del context.user_data["expense_data"]
                
                # Mostrar el menú principal
                return await _show_menu(update, context)
            else:
                # Si hubo un error en la creación, mostrar mensaje de error
                error_message = response_data.get("error", "Error desconocido")
                await send_error(update, context, f"Error al crear el gasto: {error_message}")
                return ConversationHandler.END
        elif response == "❌ Cancelar":
            # Si el usuario elige cancelar explícitamente
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            
            # Limpiar los datos del gasto del contexto
            if "expense_data" in context.user_data:
                del context.user_data["expense_data"]
            
            # Mostrar el menú principal
            return await _show_menu(update, context)
        else:
            # Si la respuesta no es reconocida
            await update.message.reply_text(
                "Opción no reconocida. Por favor, selecciona Confirmar o Cancelar.",
                reply_markup=Keyboards.get_confirmation_keyboard()
            )
            return CONFIRM
            
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en confirm_expense: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al confirmar el gasto.")
        return ConversationHandler.END

async def listar_gastos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lists all expenses for the user's family.
    
    This function retrieves and displays all expenses for the family
    that the user belongs to.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el ID de Telegram del usuario
        telegram_id = str(update.effective_user.id)
        
        # Verificar que el usuario pertenece a una familia
        status_code, member = MemberService.get_member(telegram_id)
        print(f"Respuesta de get_member en listar_gastos: {status_code}, {member}")
        
        if status_code != 200 or not member or not member.get("family_id"):
            # Si el usuario no está en una familia, mostrar error
            await update.message.reply_text(
                Messages.ERROR_NOT_IN_FAMILY,
                reply_markup=Keyboards.remove_keyboard()
            )
            return ConversationHandler.END
            
        # Obtener el ID de la familia del usuario
        family_id = member.get("family_id")
        
        # Intentar obtener los nombres de los miembros desde el contexto
        member_names = context.user_data.get("member_names", {})
        
        # Si no hay nombres en el contexto, intentar cargarlos desde la familia
        if not member_names:
            print("No se encontraron nombres de miembros en el contexto. Cargando desde la API...")
            # Obtener información de la familia completa para tener la lista de miembros
            status_code, family = FamilyService.get_family(family_id, telegram_id)
            print(f"Respuesta de get_family en listar_gastos: {status_code}, {family}")
            
            if status_code == 200 and family and "members" in family:
                # Crear diccionario de ID -> nombre para los miembros
                member_names = {}
                for family_member in family.get("members", []):
                    member_id = family_member.get("id")
                    member_name = family_member.get("name", f"Usuario {member_id}")
                    print(f"Procesando miembro: ID={member_id} ({type(member_id)}), Nombre={member_name}")
                    
                    # Guardar el ID como string siempre
                    member_names[str(member_id)] = member_name
                    
                    # Si el ID es un número o puede convertirse a número, también guardarlo como número
                    if isinstance(member_id, int) or (isinstance(member_id, str) and member_id.isdigit()):
                        numeric_id = int(member_id) if isinstance(member_id, str) else member_id
                        member_names[numeric_id] = member_name
                
                # Guardar los nombres en el contexto para futuros usos
                context.user_data["member_names"] = member_names
                print(f"Nombres de miembros cargados y guardados en el contexto: {member_names}")
                
                # También guardar la familia completa para referencia futura
                context.user_data["family"] = family
        
        # Obtener todos los gastos de la familia desde el servicio
        status_code, expenses = ExpenseService.get_family_expenses(family_id, telegram_id)
        print(f"Respuesta de get_family_expenses: {status_code}, {expenses}")
        
        if status_code != 200:
            # Si hubo un error al obtener los gastos, mostrar mensaje de error
            error_message = expenses.get("error", "Error desconocido")
            await send_error(update, context, f"Error al obtener los gastos: {error_message}")
            return await _show_menu(update, context)
            
        # Verificar si la familia tiene gastos registrados
        if not expenses or len(expenses) == 0:
            await update.message.reply_text(
                Messages.NO_EXPENSES,
                parse_mode="Markdown"
            )
            return await _show_menu(update, context)
            
        # Preparar el mensaje con la lista de gastos
        message = Messages.EXPENSES_LIST_HEADER
        
        # Ordenar los gastos por fecha (más recientes primero)
        expenses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Iterar sobre cada gasto para formatear la información
        for expense in expenses:
            expense_id = expense.get("id")
            description = expense.get("description", "Sin descripción")
            amount = expense.get("amount", 0)
            paid_by_id = expense.get("paid_by")
            created_at = expense.get("created_at", "")
            
            print(f"Procesando gasto: ID={expense_id}, pagado por ID={paid_by_id} ({type(paid_by_id)})")
            
            # Intentar buscar el nombre del miembro de diferentes maneras
            paid_by_name = None
            
            # 1. Buscar como string (el caso más común y seguro)
            if paid_by_id is not None:
                str_id = str(paid_by_id)
                if str_id in member_names:
                    paid_by_name = member_names[str_id]
                    print(f"Nombre encontrado usando string ID: {paid_by_name}")
            
            # 2. Buscar como número si es aplicable
            if not paid_by_name and paid_by_id is not None:
                if isinstance(paid_by_id, int) or (isinstance(paid_by_id, str) and paid_by_id.isdigit()):
                    numeric_id = int(paid_by_id) if isinstance(paid_by_id, str) else paid_by_id
                    if numeric_id in member_names:
                        paid_by_name = member_names[numeric_id]
                        print(f"Nombre encontrado usando numeric ID: {paid_by_name}")
            
            # 3. Buscar directamente en los miembros de la familia
            if not paid_by_name and "family" in context.user_data and "members" in context.user_data["family"]:
                for family_member in context.user_data["family"]["members"]:
                    member_id = family_member.get("id")
                    # Comparar como strings para mayor seguridad
                    if str(member_id) == str(paid_by_id):
                        paid_by_name = family_member.get("name")
                        print(f"Nombre encontrado en familia directamente: {paid_by_name}")
                        break
            
            # 4. Valor por defecto si no se encuentra
            if not paid_by_name:
                paid_by_name = f"Usuario {paid_by_id}"
                print(f"No se encontró nombre, usando valor por defecto: {paid_by_name}")
                
            # Formatear la fecha de creación del gasto
            formatted_date = Formatters.format_date(created_at)
            
            # Añadir la información del gasto al mensaje
            message += Messages.EXPENSE_LIST_ITEM.format(
                id=expense_id,
                description=description,
                amount=Formatters.format_currency(amount),
                paid_by=paid_by_name,
                date=formatted_date
            )
            
        # Enviar el mensaje con la lista de gastos
        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )
        
        # Mostrar el menú principal
        return await _show_menu(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en listar_gastos: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al listar los gastos.")
        return await _show_menu(update, context) 