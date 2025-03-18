"""
Expense Handler Module

This module handles all expense-related operations in the bot, including
creating new expenses, listing existing expenses, and managing expense data.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import DESCRIPTION, AMOUNT, SELECT_MEMBERS, CONFIRM, logger
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
            "family_id": member.get("family_id"),
            "member_name": member.get("name", update.effective_user.first_name)  # Guardar el nombre del usuario
        }
        
        # También actualizar o crear la caché de nombres de miembros
        if "member_names" not in context.user_data:
            context.user_data["member_names"] = {}
        
        # Guardar el nombre del miembro actual en la caché
        member_id = member.get("id")
        if member_id:
            context.user_data["member_names"][str(member_id)] = member.get("name", update.effective_user.first_name)
        
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
    then shows options for how to divide the expense.
    
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
        
        # Mostrar opciones de división del gasto
        return await show_expense_division_options(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en get_expense_amount: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al procesar el monto del gasto.")
        return ConversationHandler.END

async def show_expense_division_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows options for how to divide the expense among family members.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener datos del gasto del contexto
        expense_data = context.user_data.get("expense_data", {})
        amount = expense_data.get("amount", 0)
        
        # Mostrar mensaje con opciones de división
        await update.message.reply_text(
            Messages.CREATE_EXPENSE_DIVISION.format(amount=amount),
            parse_mode="Markdown",
            reply_markup=Keyboards.get_expense_division_keyboard()
        )
        
        # Pasar al siguiente estado: seleccionar miembros
        return SELECT_MEMBERS
        
    except Exception as e:
        print(f"Error en show_expense_division_options: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al mostrar las opciones de división del gasto.")
        return ConversationHandler.END

async def select_members_for_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selection of members to share an expense with.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener la opción seleccionada por el usuario
        selection = update.message.text.strip()
        
        # Verificar si el usuario quiere cancelar la operación
        if selection == "❌ Cancelar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            # Limpiar datos temporales
            if "expense_data" in context.user_data:
                del context.user_data["expense_data"]
            return await _show_menu(update, context)
        
        # Obtener datos del gasto y de la familia
        expense_data = context.user_data.get("expense_data", {})
        family_id = expense_data.get("family_id")
        telegram_id = expense_data.get("telegram_id")
        current_member_id = expense_data.get("member_id")
        
        # Si el usuario elige dividir entre todos (opción por defecto)
        if selection == "👥 Dividir entre todos (por defecto)":
            # No es necesario especificar split_among, se usará a todos los miembros por defecto
            expense_data["split_among"] = None
            context.user_data["expense_data"] = expense_data
            
            # Mostrar confirmación directamente
            return await show_expense_confirmation(update, context)
        
        # Si el usuario elige seleccionar miembros específicos
        elif selection == "👤 Seleccionar miembros específicos":
            # Obtener la lista de miembros de la familia
            members_status, members = FamilyService.get_family_members(family_id, token=telegram_id)
            
            if members_status != 200 or not members:
                await update.message.reply_text(
                    "No se pudo obtener la lista de miembros de la familia. Por favor, intenta nuevamente.",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            # Guardar la lista completa de miembros en el contexto para uso futuro
            context.user_data["family_members"] = members
            
            # Actualizar la caché de nombres con todos los miembros
            if "member_names" not in context.user_data:
                context.user_data["member_names"] = {}
            
            for member in members:
                member_id = member.get("id")
                member_name = member.get("name", f"Usuario {member_id}")
                if member_id:
                    context.user_data["member_names"][str(member_id)] = member_name
            
            # Filtrar los miembros para excluir al creador del gasto
            filtered_members = [member for member in members if str(member.get("id")) != str(current_member_id)]
            
            # Inicializar la lista de miembros seleccionados (sin incluir al creador)
            # El creador siempre se incluirá automáticamente al final
            selected_members = []
            expense_data["selected_members"] = selected_members
            context.user_data["expense_data"] = expense_data
            
            # Mostrar mensaje explicativo y el teclado de selección de miembros
            message = (
                "👥 Selecciona los miembros que compartirán este gasto:\n\n"
                "Toca sobre un nombre para seleccionar/deseleccionar\n"
                "- Los nombres con ✅ están seleccionados\n"
                "- Los nombres con ⬜ no están seleccionados\n\n"
                "🔹 Tú siempre estás incluido automáticamente en el gasto\n\n"
                "Cuando termines, presiona \"✓ Continuar\""
            )
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.get_select_members_keyboard(filtered_members, selected_members)
            )
            
            # Mantener el mismo estado para permitir la selección de miembros
            return SELECT_MEMBERS
            
        # Si el usuario está en el proceso de selección de miembros
        elif selection.startswith("✅ ") or selection.startswith("⬜ "):
            # Verificar si tenemos la lista de miembros en el contexto
            if "family_members" not in context.user_data:
                # Si no tenemos la lista, obtenerla nuevamente
                members_status, members = FamilyService.get_family_members(family_id, token=telegram_id)
                
                if members_status != 200 or not members:
                    await update.message.reply_text(
                        "No se pudo obtener la lista de miembros de la familia. Por favor, intenta nuevamente.",
                        reply_markup=Keyboards.get_main_menu_keyboard()
                    )
                    return ConversationHandler.END
                
                context.user_data["family_members"] = members
            else:
                members = context.user_data["family_members"]
            
            # Filtrar para excluir al creador
            filtered_members = [member for member in members if str(member.get("id")) != str(current_member_id)]
            
            # Obtener la lista actual de miembros seleccionados
            selected_members = expense_data.get("selected_members", [])
            
            # Encontrar el miembro correspondiente a la selección
            member_name = selection[2:].strip()  # Quitar el prefijo (✅ o ⬜)
            selected_member_id = None
            
            for member in filtered_members:
                if member.get("name") == member_name:
                    selected_member_id = str(member.get("id"))
                    break
            
            if selected_member_id:
                # Alternar la selección del miembro
                if selected_member_id in selected_members:
                    selected_members.remove(selected_member_id)
                else:
                    selected_members.append(selected_member_id)
                
                # Actualizar la selección en el contexto
                expense_data["selected_members"] = selected_members
                context.user_data["expense_data"] = expense_data
                
                # Mostrar el teclado actualizado
                await update.message.reply_text(
                    "Selección actualizada. Continúa seleccionando miembros o presiona \"✓ Continuar\" cuando termines.",
                    reply_markup=Keyboards.get_select_members_keyboard(filtered_members, selected_members)
                )
            
            # Mantener el mismo estado para continuar la selección
            return SELECT_MEMBERS
            
        # Si el usuario selecciona "Seleccionar todos"
        elif selection == "✅ Seleccionar todos":
            # Verificar si tenemos la lista de miembros en el contexto
            if "family_members" not in context.user_data:
                # Si no tenemos la lista, obtenerla nuevamente
                members_status, members = FamilyService.get_family_members(family_id, token=telegram_id)
                
                if members_status != 200 or not members:
                    await update.message.reply_text(
                        "No se pudo obtener la lista de miembros de la familia. Por favor, intenta nuevamente.",
                        reply_markup=Keyboards.get_main_menu_keyboard()
                    )
                    return ConversationHandler.END
                
                context.user_data["family_members"] = members
            else:
                members = context.user_data["family_members"]
            
            # Filtrar para excluir al creador
            filtered_members = [member for member in members if str(member.get("id")) != str(current_member_id)]
            
            # Seleccionar todos los miembros (excepto el creador, que ya está incluido automáticamente)
            selected_members = [str(member.get("id")) for member in filtered_members if member.get("id")]
            
            # Actualizar la selección en el contexto
            expense_data["selected_members"] = selected_members
            context.user_data["expense_data"] = expense_data
            
            # Mostrar el teclado actualizado
            await update.message.reply_text(
                "Se han seleccionado todos los miembros. Presiona \"✓ Continuar\" cuando estés listo.",
                reply_markup=Keyboards.get_select_members_keyboard(filtered_members, selected_members)
            )
            
            # Mantener el mismo estado para continuar la selección
            return SELECT_MEMBERS
            
        # Si el usuario selecciona "Deseleccionar todos"
        elif selection == "⬜ Deseleccionar todos":
            # Verificar si tenemos la lista de miembros en el contexto
            if "family_members" not in context.user_data:
                # Si no tenemos la lista, obtenerla nuevamente
                members_status, members = FamilyService.get_family_members(family_id, token=telegram_id)
                
                if members_status != 200 or not members:
                    await update.message.reply_text(
                        "No se pudo obtener la lista de miembros de la familia. Por favor, intenta nuevamente.",
                        reply_markup=Keyboards.get_main_menu_keyboard()
                    )
                    return ConversationHandler.END
                
                context.user_data["family_members"] = members
            else:
                members = context.user_data["family_members"]
            
            # Filtrar para excluir al creador
            filtered_members = [member for member in members if str(member.get("id")) != str(current_member_id)]
            
            # Deseleccionar todos los miembros
            expense_data["selected_members"] = []
            context.user_data["expense_data"] = expense_data
            
            # Mostrar el teclado actualizado
            await update.message.reply_text(
                "Se han deseleccionado todos los miembros. El gasto será solo para ti a menos que selecciones a otros miembros.",
                reply_markup=Keyboards.get_select_members_keyboard(filtered_members, [])
            )
            
            # Mantener el mismo estado para continuar la selección
            return SELECT_MEMBERS
            
        # Si el usuario selecciona "Continuar"
        elif selection == "✓ Continuar":
            # Obtener la lista actual de miembros seleccionados
            selected_members = expense_data.get("selected_members", [])
            
            # Incluir al creador del gasto siempre en la lista de split_among
            final_split_among = selected_members.copy()
            if str(current_member_id) not in final_split_among:
                final_split_among.append(str(current_member_id))
            
            # Guardar la lista final de miembros seleccionados para el API
            expense_data["split_among"] = final_split_among
            context.user_data["expense_data"] = expense_data
            
            # Mostrar confirmación
            return await show_expense_confirmation(update, context)
            
        # Si la respuesta no es reconocida, pedir que seleccione una opción válida
        else:
            await update.message.reply_text(
                "Por favor, selecciona una opción válida.",
                reply_markup=Keyboards.get_expense_division_keyboard()
            )
            return SELECT_MEMBERS
            
    except Exception as e:
        print(f"Error en select_members_for_expense: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al seleccionar los miembros para el gasto.")
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
    try:
        # Obtener los datos del gasto del contexto del usuario
        expense_data = context.user_data.get("expense_data", {})
        description = expense_data.get("description", "")
        amount = expense_data.get("amount", 0)
        
        # Determinar cómo se dividirá el gasto
        split_among = expense_data.get("split_among")
        
        # Preparar el texto para mostrar cómo se divide el gasto
        if split_among is None:
            split_text = "Todos los miembros de la familia"
        else:
            # Obtener los nombres de los miembros seleccionados
            member_names = []
            
            for member_id in split_among:
                # Primero intentar obtener el nombre de la caché
                if "member_names" in context.user_data and member_id in context.user_data["member_names"]:
                    name = context.user_data["member_names"][member_id]
                    member_names.append(name)
                # Luego intentar buscar en la lista de miembros de la familia
                elif "family_members" in context.user_data:
                    for member in context.user_data["family_members"]:
                        if str(member.get("id")) == str(member_id):
                            name = member.get("name", f"Usuario {member_id}")
                            member_names.append(name)
                            break
                else:
                    # Si no se encuentra el nombre, usar el ID
                    member_names.append(f"Usuario {member_id}")
            
            # Crear el texto con los nombres
            if member_names:
                split_text = ", ".join(member_names)
            else:
                split_text = "Error: no se encontraron miembros seleccionados"
        
        # Mostrar mensaje de confirmación con los detalles del gasto
        await update.message.reply_text(
            Messages.CREATE_EXPENSE_CONFIRM.format(
                description=description,
                amount=amount,
                paid_by="Tú",
                split_among=split_text
            ),
            parse_mode="Markdown",
            reply_markup=Keyboards.get_confirmation_keyboard()
        )
        
        # Pasar al siguiente estado: confirmar gasto
        return CONFIRM
        
    except Exception as e:
        print(f"Error en show_expense_confirmation: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, "Ocurrió un error al mostrar la confirmación del gasto.")
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

async def confirm_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's confirmation of a new expense.
    
    This function processes the user's confirmation or cancellation of 
    an expense creation operation. If confirmed, it creates a new expense
    in the database.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener la respuesta del usuario (confirmar o cancelar)
        response = update.message.text.strip()
        
        # Obtener los datos del gasto del contexto
        expense_data = context.user_data.get("expense_data", {})
        
        # Procesar según la respuesta
        if response == "✅ Confirmar":
            # Si el usuario confirma, crear el gasto
            description = expense_data.get("description")
            amount = expense_data.get("amount")
            
            # Obtener el ID del miembro que paga - puede estar en member_id (clave inicial)
            member_id = expense_data.get("member_id")
            paid_by = expense_data.get("paid_by", member_id)  # Usar member_id como fallback
            
            # Asegurar que tengamos un paid_by válido
            if not paid_by and member_id:
                paid_by = member_id
            
            family_id = expense_data.get("family_id")
            telegram_id = expense_data.get("telegram_id")
            split_among = expense_data.get("split_among") # Lista de IDs o None (todos)
            
            # Verificar que tenemos todos los datos necesarios
            if not all([description, amount, paid_by, family_id]):
                await update.message.reply_text(
                    "Faltan datos para crear el gasto. Por favor, inténtalo de nuevo.",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            # Crear el gasto a través del servicio
            status_code, response = ExpenseService.create_expense(
                description=description,
                amount=amount,
                paid_by=paid_by,
                family_id=family_id,
                telegram_id=telegram_id,
                split_among=split_among
            )
            
            # Procesar según el resultado
            if status_code in [200, 201]:
                # Si se creó correctamente, mostrar mensaje de éxito
                await update.message.reply_text(
                    Messages.SUCCESS_EXPENSE_CREATED,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
                # Notificar a todos los miembros de la familia sobre el nuevo gasto
                try:
                    # Obtener la información completa del gasto creado
                    expense_id = response.get("id")
                    created_at = response.get("created_at", "desconocida")
                    
                    # Formatear la fecha si está disponible
                    if isinstance(created_at, str) and "T" in created_at:
                        date_part = created_at.split("T")[0]
                        created_at = date_part
                    
                    # Obtener el nombre del miembro que pagó - Simplificar usando el contexto
                    paid_by_name = "Desconocido"
                    
                    # Si el pagador es el usuario actual, usar el nombre guardado en expense_data
                    if str(paid_by) == str(expense_data.get("member_id")):
                        paid_by_name = expense_data.get("member_name", update.effective_user.first_name)
                        logger.info(f"[NOTIFY_EXPENSE] Usando nombre del creador del gasto: {paid_by_name}")
                    # Si no es el usuario actual, intentar obtenerlo de la caché de nombres
                    elif "member_names" in context.user_data and str(paid_by) in context.user_data["member_names"]:
                        paid_by_name = context.user_data["member_names"][str(paid_by)]
                        logger.info(f"[NOTIFY_EXPENSE] Nombre encontrado en caché: {paid_by_name}")
                    # Solo si no está en caché, buscar en la familia
                    else:
                        logger.info(f"[NOTIFY_EXPENSE] Buscando nombre en la familia para ID: {paid_by}")
                        # Intentar obtener de la familia en caché
                        if "family" in context.user_data and "members" in context.user_data["family"]:
                            for member in context.user_data["family"]["members"]:
                                if str(member.get("id")) == str(paid_by):
                                    paid_by_name = member.get("name", "Desconocido")
                                    logger.info(f"[NOTIFY_EXPENSE] Nombre encontrado en familia: {paid_by_name}")
                                    
                                    # Actualizar caché
                                    if "member_names" not in context.user_data:
                                        context.user_data["member_names"] = {}
                                    context.user_data["member_names"][str(paid_by)] = paid_by_name
                                    break
                    
                    # Determinar los miembros que deben recibir la notificación
                    # Si split_among es None, notificar a todos los miembros de la familia
                    # Si no, notificar solo a los miembros incluidos en split_among
                    members_to_notify = []
                    
                    # Obtener la lista de miembros de la familia
                    logger.info(f"[NOTIFY_EXPENSE] Obteniendo miembros de la familia {family_id} para notificar sobre nuevo gasto")
                    members_status, members = FamilyService.get_family_members(family_id, token=telegram_id)
                    
                    if members_status == 200 and members:
                        # Actualizar caché de nombres y guardar la familia para uso futuro
                        if paid_by_name == "Desconocido":
                            for member in members:
                                if str(member.get("id")) == str(paid_by):
                                    paid_by_name = member.get("name", "Desconocido")
                                    logger.info(f"[NOTIFY_EXPENSE] Nombre encontrado en miembros obtenidos: {paid_by_name}")
                                    break
                        
                        # Actualizar la caché de nombres con todos los miembros
                        if "member_names" not in context.user_data:
                            context.user_data["member_names"] = {}
                        
                        for member in members:
                            member_id = member.get("id")
                            member_name = member.get("name", f"Usuario {member_id}")
                            if member_id:
                                context.user_data["member_names"][str(member_id)] = member_name
                        
                        # Guardar la familia en el contexto para uso futuro
                        context.user_data["family"] = {"members": members}
                        
                        # Filtrar los miembros que deberían recibir la notificación
                        if split_among is None:
                            # Si se divide entre todos, notificar a todos
                            members_to_notify = members
                        else:
                            # Si se divide entre miembros específicos, filtrar la lista
                            for member in members:
                                member_id = str(member.get("id"))
                                if member_id in split_among:
                                    members_to_notify.append(member)
                        
                        # Crear texto que indique cómo se dividió el gasto
                        split_text = ""
                        if split_among is None:
                            split_text = "*Dividido entre:* Todos los miembros\n"
                        else:
                            # Crear lista de nombres
                            member_names_list = []
                            for member_id in split_among:
                                name = None
                                # Buscar en la caché de nombres
                                if member_id in context.user_data["member_names"]:
                                    name = context.user_data["member_names"][member_id]
                                
                                # Si no se encuentra en la caché, buscar en los miembros
                                if not name:
                                    for member in members:
                                        if str(member.get("id")) == member_id:
                                            name = member.get("name", f"Usuario {member_id}")
                                            break
                                
                                if name:
                                    member_names_list.append(name)
                                else:
                                    member_names_list.append(f"Usuario {member_id}")
                            
                            split_text = f"*Dividido entre:* {', '.join(member_names_list)}\n"
                        
                        # Formatear el mensaje de notificación
                        notification_message = (
                            f"💸 *Nuevo Gasto Registrado*\n\n"
                            f"*Descripción:* {description}\n"
                            f"*Monto:* ${amount:.2f}\n"
                            f"*Pagado por:* {paid_by_name}\n"
                            f"{split_text}"
                            f"*Fecha:* {created_at}\n\n"
                            f"_Gasto registrado en la familia por {update.effective_user.first_name}_"
                        )
                        
                        # Enviar mensaje a cada miembro seleccionado
                        current_user_id = str(update.effective_user.id)
                        notified_count = 0
                        
                        for member in members_to_notify:
                            member_telegram_id = member.get("telegram_id")
                            
                            # No enviar notificación al usuario que creó el gasto (ya recibió confirmación)
                            if member_telegram_id and member_telegram_id != current_user_id:
                                try:
                                    await context.bot.send_message(
                                        chat_id=member_telegram_id,
                                        text=notification_message,
                                        parse_mode="Markdown"
                                    )
                                    notified_count += 1
                                    logger.info(f"[NOTIFY_EXPENSE] Notificación enviada a miembro {member.get('name')} (ID: {member_telegram_id})")
                                except Exception as notify_error:
                                    logger.error(f"[NOTIFY_EXPENSE] Error al notificar a miembro {member_telegram_id}: {str(notify_error)}")
                        
                        if notified_count > 0:
                            logger.info(f"[NOTIFY_EXPENSE] Se notificó a {notified_count} miembros sobre el nuevo gasto")
                    else:
                        logger.warning(f"[NOTIFY_EXPENSE] No se pudo obtener la lista de miembros. Status: {members_status}")
                
                except Exception as notify_error:
                    logger.error(f"[NOTIFY_EXPENSE] Error en proceso de notificación: {str(notify_error)}")
                    traceback.print_exc()
                    # No bloqueamos el flujo principal si la notificación falla
                
                # Limpiar los datos del gasto del contexto
                if "expense_data" in context.user_data:
                    del context.user_data["expense_data"]
                
                # Finalizar conversación
                return ConversationHandler.END
            else:
                # Si hubo un error, mostrar el mensaje de error
                error_message = "Error desconocido"
                if isinstance(response, dict) and "detail" in response:
                    error_message = response["detail"]
                
                await update.message.reply_text(
                    f"❌ Error al crear el gasto: {error_message}",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
        
        elif response == "❌ Cancelar":
            # Si el usuario cancela, mostrar mensaje de cancelación
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            
            # Limpiar los datos del gasto del contexto
            if "expense_data" in context.user_data:
                del context.user_data["expense_data"]
            
            # Finalizar conversación
            return ConversationHandler.END
        
        else:
            # Si la respuesta no es reconocida, pedir que seleccione una opción válida
            await update.message.reply_text(
                "Por favor, selecciona 'Confirmar' o 'Cancelar'.",
                reply_markup=Keyboards.get_confirmation_keyboard()
            )
            return CONFIRM
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en confirm_expense: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al confirmar el gasto: {str(e)}")
        return ConversationHandler.END 