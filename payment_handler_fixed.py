"""
Módulo para manejar la funcionalidad de pagos entre miembros.

Este módulo contiene las funciones para registrar pagos entre miembros de una familia,
seleccionar montos, destinatarios y confirmar transacciones.
"""

import re
import traceback
from typing import Dict, List, Tuple, Any
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services.payment_service import PaymentService
from services.member_service import MemberService
from services.family_service import FamilyService
from ui.keyboards import Keyboards
from ui.messages import Messages
from config import (
    SELECT_TO_MEMBER,
    PAYMENT_AMOUNT,
    PAYMENT_CONFIRM,
    logger
)
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
        
        # Verificar si el usuario pertenece a una familia
        status_code, member = MemberService.get_member(telegram_id)
        
        # Si el usuario no está en una familia, mostrar error y terminar
        if status_code != 200 or not member or not member.get("family_id"):
            await update.message.reply_text(
                Messages.ERROR_NOT_IN_FAMILY,
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Obtener el ID de la familia y datos del miembro
        family_id = member.get("family_id")
        from_member_id = member.get("id")
        from_member_name = member.get("name", "Tú")
        
        # Guardar datos iniciales en el contexto
        context.user_data["payment_data"]["from_member_id"] = from_member_id
        context.user_data["payment_data"]["from_member_name"] = from_member_name
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
        
        # Obtener los balances de la familia
        status_code, balances = FamilyService.get_family_balances(family_id, telegram_id)
        
        # Crear diccionarios para mapear miembros a sus saldos
        balances_dict = {}  # Lo que otros te deben a ti
        debts_dict = {}     # Lo que tú debes a otros
        
        # Crear mapeos para facilitar referencias
        id_to_name = {m.get("id"): m.get("name", "Desconocido") for m in members}
        
        if status_code == 200 and balances:
            # Buscamos los balances específicos para el usuario actual
            for balance in balances:
                # Si este balance corresponde al usuario actual
                if str(balance.get("member_id")) == str(from_member_id):
                    # Procesar sus deudas (lo que debe a otros)
                    for debt in balance.get("debts", []):
                        to_name = debt.get("to")
                        amount = debt.get("amount", 0)
                        
                        # Buscar el ID del miembro por su nombre
                        to_id = None
                        for member in members:
                            if member.get("name") == to_name:
                                to_id = member.get("id")
                                break
                        
                        if to_id and amount > 0:
                            debts_dict[str(to_id)] = amount
                            
                    # Procesar sus créditos (lo que otros le deben)
                    for credit in balance.get("credits", []):
                        from_name = credit.get("from")
                        amount = credit.get("amount", 0)
                        
                        # Buscar el ID del miembro por su nombre
                        from_id = None
                        for member in members:
                            if member.get("name") == from_name:
                                from_id = member.get("id")
                                break
                        
                        if from_id and amount > 0:
                            balances_dict[str(from_id)] = amount
                    
                    break  # Una vez encontrado el balance del usuario, salimos del bucle
        
        # Guardar datos en el contexto
        context.user_data["payment_data"]["members"] = members
        context.user_data["payment_data"]["other_members"] = other_members
        context.user_data["payment_data"]["balances"] = balances_dict
        context.user_data["payment_data"]["debts"] = debts_dict
        
        # Mostrar resumen de deudas si existen
        deudas_mensaje = ""
        if debts_dict:
            deudas_lista = []
            for creditor_id, amount in debts_dict.items():
                creditor_name = id_to_name.get(creditor_id, f"Usuario {creditor_id}")
                deudas_lista.append(f"• Debes ${amount:.2f} a {creditor_name}")
            deudas_mensaje = "📊 *Resumen de tus deudas:*\n" + "\n".join(deudas_lista) + "\n\n"
        else:
            # Si el usuario no tiene deudas, mostrar mensaje y regresar al menú principal
            await update.message.reply_text(
                Messages.NO_DEBTS,
                parse_mode="Markdown",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Crear teclado con los nombres de los miembros
        member_buttons = []
        
        # Filtrar miembros para mostrar solo aquellos a los que el usuario debe dinero
        members_with_debt = []
        
        for member in other_members:
            member_id = str(member.get("id"))
            member_name = member.get("name", "Desconocido")
            
            # Verificar si hay deuda pendiente con este miembro
            debt_amount = debts_dict.get(member_id, 0)
            
            # Solo considerar miembros a los que se les debe dinero
            if debt_amount > 0:
                members_with_debt.append({
                    "id": member_id,
                    "name": member_name,
                    "debt_amount": debt_amount
                })
                # Mostrar solo el nombre del miembro y su deuda
                button_text = f"{member_name} - ${debt_amount:.2f}"
                member_buttons.append([button_text])
        
        # Verificar si después del filtrado queda algún miembro para mostrar
        if not members_with_debt:
            # Caso especial: hay deudas pero no con los miembros actuales de la familia
            await update.message.reply_text(
                "No se encontraron miembros en tu familia a los que debas dinero actualmente.",
                parse_mode="Markdown",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Agregar botón de cancelar
        member_buttons.append(["❌ Cancelar"])
        
        # Guardar la lista filtrada de miembros con deuda para uso futuro
        context.user_data["payment_data"]["members_with_debt"] = members_with_debt
        
        # Mostrar mensaje para seleccionar el destinatario del pago
        await update.message.reply_text(
            deudas_mensaje + Messages.SELECT_PAYMENT_RECIPIENT,
            reply_markup=ReplyKeyboardMarkup(
                member_buttons, 
                one_time_keyboard=True,
                resize_keyboard=True
            ),
            parse_mode="Markdown"
        )
        
        # Pasar al siguiente estado: seleccionar destinatario
        return SELECT_TO_MEMBER
        
    except Exception as e:
        await send_error(update, context, f"Error al iniciar el registro de pago: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def select_to_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selection of the payment recipient and payment type.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el texto completo seleccionado
        selected_text = update.message.text
        
        # Verificar si el usuario canceló la operación
        if selected_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
    
        # Verificar si ya tenemos un miembro seleccionado en el contexto
        payment_data = context.user_data.get("payment_data", {})
        to_member_id = payment_data.get("to_member_id")
        
        if to_member_id:
            # Ya tenemos un miembro seleccionado, procesamos la selección del tipo de pago
            to_member_name = payment_data.get("to_member_name")
            debt_amount = payment_data.get("debt_amount", 0)
            
            if selected_text == "Pago Parcial":
                # Si es pago parcial, continuar con el flujo normal para pedir el monto
                message_text = Messages.CREATE_PAYMENT_AMOUNT.format(to_member=to_member_name)
                
                # Añadir la deuda actual y sugerir ese monto para el pago
                message_text += f"\n\n💡 Deuda actual: ${debt_amount:.2f}"
                message_text += f"\n\n💰 *Sugerencia:* Puedes escribir \"{debt_amount:.2f}\" para pagar la deuda completa."
                
                await update.message.reply_text(
                    message_text,
                    parse_mode="Markdown",
                    reply_markup=Keyboards.get_cancel_keyboard()
                )
                
                # Pasar al siguiente estado: ingresar monto
                return PAYMENT_AMOUNT
                
            elif selected_text == f"Pago Total: ${debt_amount:.2f}":
                # Si es un pago total, establecer el monto directamente y pasar a confirmación
                context.user_data["payment_data"]["amount"] = debt_amount
                # Ir directamente a la confirmación
                return await show_payment_confirmation(update, context)
                
            else:
                # Opción no válida, volver a mostrar las opciones de pago
                payment_options = [
                    ["Pago Parcial"],
                    [f"Pago Total: ${debt_amount:.2f}"],
                    ["❌ Cancelar"]
                ]
                
                await update.message.reply_text(
                    f"Opción no válida. Por favor, selecciona un tipo de pago para {to_member_name}:",
                    reply_markup=ReplyKeyboardMarkup(
                        payment_options,
                        one_time_keyboard=True,
                        resize_keyboard=True
                    )
                )
                
                return SELECT_TO_MEMBER
        else:
            # No tenemos un miembro seleccionado, procesamos la selección del miembro
            
            # Recuperar la lista filtrada de miembros con deuda
            members_with_debt = context.user_data.get("payment_data", {}).get("members_with_debt", [])
            
            # Extraer el nombre del miembro del texto seleccionado
            # El formato es "nombre - $XX.XX"
            parts = selected_text.split(" - ")
            if len(parts) < 2:
                # Formato incorrecto, volver a mostrar las opciones
                buttons = []
                for member in members_with_debt:
                    member_name = member.get("name")
                    debt_amount = member.get("debt_amount", 0)
                    button_text = f"{member_name} - ${debt_amount:.2f}"
                    buttons.append([button_text])
                buttons.append(["❌ Cancelar"])
                
                await update.message.reply_text(
                    "Opción no válida. Por favor, selecciona un miembro de la lista:",
                    reply_markup=ReplyKeyboardMarkup(
                        buttons,
                        one_time_keyboard=True,
                        resize_keyboard=True
                    )
                )
                return SELECT_TO_MEMBER
                
            member_name = parts[0]
            
            # Buscar el miembro por nombre
            selected_member = None
            for member in members_with_debt:
                if member.get("name") == member_name:
                    selected_member = member
                    break
    
            if not selected_member:
                # Si no se encuentra el miembro, mostrar error y volver a pedir
                buttons = []
                for member in members_with_debt:
                    member_name = member.get("name")
                    debt_amount = member.get("debt_amount", 0)
                    button_text = f"{member_name} - ${debt_amount:.2f}"
                    buttons.append([button_text])
                buttons.append(["❌ Cancelar"])
                
                await update.message.reply_text(
                    f"Miembro '{member_name}' no encontrado. Por favor, selecciona un miembro de la lista:",
                    reply_markup=ReplyKeyboardMarkup(
                        buttons,
                        one_time_keyboard=True,
                        resize_keyboard=True
                    )
                )
                return SELECT_TO_MEMBER
    
            # Guardar el ID del miembro destinatario en el contexto
            to_member_id = selected_member.get("id")
            to_member_name = selected_member.get("name")
            debt_amount = selected_member.get("debt_amount", 0)
            context.user_data["payment_data"]["to_member_id"] = to_member_id
            context.user_data["payment_data"]["to_member_name"] = to_member_name
            context.user_data["payment_data"]["debt_amount"] = debt_amount
            
            # Ahora que se seleccionó el miembro, mostrar las opciones de pago
            payment_options = [
                ["Pago Parcial"],
                [f"Pago Total: ${debt_amount:.2f}"],
                ["❌ Cancelar"]
            ]
    
            await update.message.reply_text(
                f"Has seleccionado a *{to_member_name}*.\nDeuda actual: ${debt_amount:.2f}\n\n¿Qué tipo de pago deseas realizar?",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    payment_options,
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            
            # Seguimos en el mismo estado, pero ahora esperando la selección del tipo de pago
            return SELECT_TO_MEMBER
        
    except Exception as e:
        await send_error(update, context, f"Error al seleccionar el destinatario o tipo de pago: {str(e)}")
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
        input_text = update.message.text.strip()
        
        # Recuperar la información de deuda almacenada en el contexto
        payment_data = context.user_data.get("payment_data", {})
        to_member_id = payment_data.get("to_member_id")
        to_member_name = payment_data.get("to_member_name")
        debt_amount = payment_data.get("debt_amount", 0)
        
        # Verificar si el usuario canceló la operación
        if input_text == "❌ Cancelar":
            await update.message.reply_text(
                "Has cancelado el registro de pago.",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
            
        # Verificar primero si es alguna de nuestras opciones especiales
        if input_text.startswith(f"✅ Pagar ${debt_amount:.2f}"):
            # El usuario eligió pagar el monto exacto de la deuda
            amount = debt_amount
            await update.message.reply_text(
                f"✅ Se ajustó el monto del pago a ${amount:.2f}, que es el valor exacto de la deuda con {to_member_name}.",
                parse_mode="Markdown"
            )
            
            # Guardar el monto validado en el contexto
            context.user_data["payment_data"]["amount"] = amount
            
            # Mostrar la confirmación del pago
            return await show_payment_confirmation(update, context)
            
        elif input_text == "🔄 Ingresar otro monto":
            # El usuario quiere ingresar otro monto
            await update.message.reply_text(
                f"Por favor, ingresa un monto que no exceda ${debt_amount:.2f}:",
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return PAYMENT_AMOUNT
        
        # Si no es una opción especial, intentar convertir a número
        try:
            # Reemplazar comas por puntos para manejar diferentes formatos numéricos
            amount_text = input_text.replace(',', '.').strip()
            amount = float(amount_text)
            
            # Verificar que el monto sea positivo
            if amount <= 0:
                await update.message.reply_text(
                    "El monto debe ser un número positivo. Por favor, ingresa el monto nuevamente:",
                    reply_markup=Keyboards.get_cancel_keyboard()
                )
                return PAYMENT_AMOUNT
                
            # Verificar que el monto no exceda la deuda actual
            if amount > debt_amount:
                # Si el monto es mayor, ofrecer opciones al usuario
                keyboard = [
                    [f"✅ Pagar ${debt_amount:.2f} (deuda completa)"],  # Opción para pagar la deuda exacta
                    ["🔄 Ingresar otro monto"],                         # Opción para ingresar otro monto
                    ["❌ Cancelar"]                                      # Opción para cancelar
                ]
                
                await update.message.reply_text(
                    f"⚠️ *Aviso de Pago*\n\n"
                    f"El monto ingresado (${amount:.2f}) excede tu deuda actual con {to_member_name} (${debt_amount:.2f}).\n\n"
                    f"¿Qué deseas hacer?",
                    parse_mode="Markdown",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard,
                        one_time_keyboard=True,
                        resize_keyboard=True
                    )
                )
                
                # Guardar temporalmente el monto ingresado para referencia
                context.user_data["payment_data"]["temp_amount"] = amount
                
                # Permanecemos en el mismo estado
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
        await send_error(update, context, f"Error al procesar el monto del pago: {str(e)}")
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
        from_member_name = payment_data.get("from_member_name", "Tú")
        to_member_name = payment_data.get("to_member_name")
        amount = payment_data.get("amount")
        to_member_id = payment_data.get("to_member_id")
        
        # Obtener información de deudas si existe
        debts_dict = payment_data.get("debts", {})
        debt_amount = debts_dict.get(str(to_member_id), 0)
        
        # Crear mensaje de confirmación
        confirmation_message = Messages.CREATE_PAYMENT_CONFIRM.format(
            from_member=from_member_name,
            to_member=to_member_name,
            amount=amount
        )
        
        # Añadir información sobre cómo afectará este pago a la deuda, si existe
        if debt_amount > 0:
            if amount >= debt_amount:
                confirmation_message += f"\n\n✅ Este pago cubrirá completamente tu deuda de ${debt_amount:.2f}."
            else:
                remaining = debt_amount - amount
                confirmation_message += f"\n\n⚠️ Este pago cubrirá parcialmente tu deuda de ${debt_amount:.2f}."
                confirmation_message += f"\nQuedarán pendientes: ${remaining:.2f}"
        
        await update.message.reply_text(
            confirmation_message,
            parse_mode="Markdown",
            reply_markup=Keyboards.get_confirmation_keyboard()
        )
        
        # Pasar al siguiente estado: confirmar pago
        return PAYMENT_CONFIRM
    except Exception as e:
        await send_error(update, context, f"Error al mostrar la confirmación del pago: {str(e)}")
        return ConversationHandler.END

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Confirma la creación de un pago entre miembros.
    
    Esta función procesa la confirmación del usuario para un nuevo pago,
    crea el registro en el sistema y actualiza los balances de los miembros.
    
    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener la respuesta del usuario
        response = update.message.text
        
        # Verificar la respuesta
        if response == "✅ Confirmar":
            # Obtener los datos del pago desde el contexto
            payment_data = context.user_data.get("payment_data", {})
            
            amount = payment_data.get("amount")
            from_member_id = payment_data.get("from_member_id")
            to_member_id = payment_data.get("to_member_id")
            telegram_id = payment_data.get("telegram_id")
            family_id = payment_data.get("family_id")
            debt_amount = payment_data.get("debt_amount", 0)
            
            # Si el usuario eligió "Pagar monto exacto" después de un error de exceso
            if response == "✅ Pagar monto exacto" and debt_amount > 0:
                # Ajustar el monto al valor exacto de la deuda
                amount = debt_amount
                # Actualizar el monto en el contexto
                context.user_data["payment_data"]["amount"] = amount
                
                # Informar al usuario del ajuste
                await update.message.reply_text(
                    f"✅ Se ajustó el monto del pago a ${amount:.2f}, que es el valor exacto de la deuda.",
                    parse_mode="Markdown"
                )
            
            # Validar que todos los datos requeridos estén presentes
            if not all([from_member_id, to_member_id, amount, family_id]):
                await update.message.reply_text(
                    "Faltan datos para crear el pago. Por favor, inténtalo de nuevo.",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
            
            # Crear el pago a través del servicio
            print(f"Creando pago: from={from_member_id}, to={to_member_id}, amount={amount}, telegram_id={telegram_id}")
            status_code, response_data = PaymentService.create_payment(
                from_member=from_member_id,
                to_member=to_member_id,
                amount=amount,
                telegram_id=telegram_id
            )
            
            if status_code in [200, 201]:
                # Obtener información sobre el estado del pago
                payment_status = response_data.get("status", "PENDING")
                
                # Mensaje inicial para el usuario que creó el pago
                success_message = Messages.SUCCESS_PAYMENT_CREATED
                
                # Si el pago está en estado PENDING, informar al usuario
                if payment_status == "PENDING":
                    success_message += "\n\nEl pago está pendiente de confirmación por el destinatario."
                
                # Mostrar mensaje de éxito al usuario que creó el pago
                await update.message.reply_text(
                    success_message,
                    parse_mode="Markdown",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
                try:
                    # Obtener información del miembro pagador para la notificación
                    from_member_name = ""
                    if "member_names" in context.user_data and str(from_member_id) in context.user_data["member_names"]:
                        from_member_name = context.user_data["member_names"][str(from_member_id)]
                    else:
                        status_code, from_member_data = MemberService.get_member_by_id(from_member_id)
                        if status_code == 200 and from_member_data:
                            from_member_name = from_member_data.get("name", "")
                    
                    # Obtener información del destinatario para enviar la notificación
                    print(f"Obteniendo datos del miembro receptor con ID: {to_member_id}")
                    to_member_data = None
                    to_telegram_id = None
                    to_member_name = None
                    
                    # ESTRATEGIA 1: Verificar primero la caché de nombres
                    if "member_names" in context.user_data and str(to_member_id) in context.user_data["member_names"]:
                        to_member_name = context.user_data["member_names"][str(to_member_id)]
                        print(f"Nombre del receptor encontrado en caché: {to_member_name}")
                    
                    # ESTRATEGIA 2: Buscar en los datos de la familia (si ya los tenemos cargados)
                    if "family" in context.user_data and "members" in context.user_data["family"]:
                        for member in context.user_data["family"]["members"]:
                            if str(member.get("id")) == str(to_member_id):
                                to_member_data = member
                                to_telegram_id = member.get("telegram_id")
                                to_member_name = member.get("name", to_member_name)
                                print(f"Información del receptor encontrada en familia en caché: {to_member_name}, ID: {to_telegram_id}")
                                break
                    
                    # ESTRATEGIA 3: Consultar la API para obtener los datos del miembro
                    if not to_telegram_id:
                        print(f"Consultando API para obtener información del receptor con ID: {to_member_id}")
                        token = context.user_data.get("token")
                        status_code, member_response = MemberService.get_member_by_id(to_member_id, token)
                        print(f"Respuesta de API: status_code={status_code}, data={member_response}")
                        
                        if status_code == 200 and member_response:
                            to_member_data = member_response
                            to_telegram_id = member_response.get("telegram_id")
                            to_member_name = member_response.get("name", to_member_name)
                            print(f"Información obtenida de API: {to_member_name}, ID: {to_telegram_id}")
                    
                    # ESTRATEGIA 4: Si no lo encontramos, obtener todos los miembros de la familia
                    if not to_telegram_id and family_id:
                        print(f"Último intento: obteniendo todos los miembros de la familia {family_id}")
                        status_code, family = FamilyService.get_family(family_id)
                        
                        if status_code == 200 and family and "members" in family:
                            # Guardar familia en contexto para futuras búsquedas
                            context.user_data["family"] = family
                            
                            # Buscar el miembro en la lista
                            for member in family.get("members", []):
                                if str(member.get("id")) == str(to_member_id):
                                    to_member_data = member
                                    to_telegram_id = member.get("telegram_id")
                                    to_member_name = member.get("name", "")
                                    print(f"Miembro encontrado en familia completa: {to_member_name}, ID: {to_telegram_id}")
                                    
                                    # Actualizar caché de nombres
                                    if "member_names" not in context.user_data:
                                        context.user_data["member_names"] = {}
                                    context.user_data["member_names"][str(to_member_id)] = to_member_name
                                    break
                    
                    if to_member_data or to_member_name:
                        print(f"ID de Telegram del receptor: '{to_telegram_id}', Nombre: '{to_member_name}'")
                        
                        # Verificar que el ID de Telegram es válido
                        if not to_telegram_id:
                            print("Error: El receptor no tiene un ID de Telegram válido")
                            await update.message.reply_text(
                                f"✅ Pago registrado correctamente, pero no se pudo notificar a {to_member_name} porque no tiene un ID de Telegram válido.\n\n" +
                                f"Para arreglar esto, {to_member_name} debe:\n" +
                                f"1. Iniciar sesión en el bot usando /start\n" +
                                f"2. Asegurarse de estar registrado en la familia con el mismo nombre\n",
                                parse_mode="Markdown"
                            )
                        elif to_telegram_id == telegram_id:
                            print("El remitente y el receptor son el mismo usuario, omitiendo notificación")
                        else:
                            # Formatear fecha si está disponible
                            import datetime
                            current_date = datetime.datetime.now().strftime("%d/%m/%Y")
                            payment_date = response_data.get("created_at", current_date)
                            if isinstance(payment_date, str) and "T" in payment_date:
                                payment_date = payment_date.split("T")[0].replace("-", "/")
                            
                            # Obtener ID del pago creado
                            payment_id = response_data.get("id")
                            
                            # Crear botones para confirmar o rechazar el pago
                            # Solo mostrar botones si el pago está en estado PENDING
                            if payment_status == "PENDING" and payment_id:
                                # Crear teclado inline con botones para confirmar/rechazar
                                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                                
                                # Simplificar los datos del callback para evitar exceder el límite de 64 bytes
                                # Usamos formato p:ID:a donde p=payment, ID=ID del pago, a=acción (c=confirm, r=reject)
                                confirm_data = f"p:{payment_id}:c"
                                reject_data = f"p:{payment_id}:r"
                                
                                keyboard = [
                                    [
                                        InlineKeyboardButton("✅ Confirmar Pago", callback_data=confirm_data),
                                        InlineKeyboardButton("❌ Rechazar", callback_data=reject_data)
                                    ]
                                ]
                                
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                
                                # Crear mensaje con solicitud de confirmación
                                notification_message = (
                                    f"💰 *¡Has recibido un pago pendiente de confirmación!*\n\n"
                                    f"*De:* {from_member_name}\n"
                                    f"*Monto:* ${amount:.2f}\n"
                                    f"*Fecha:* {payment_date}\n\n"
                                    f"Este pago requiere tu confirmación para ser aplicado a tu balance. "
                                    f"Por favor, confirma o rechaza este pago."
                                )
                            else:
                                # Si el pago ya está confirmado, no mostrar botones
                                reply_markup = None
                                
                                # Crear mensaje de notificación estándar
                                notification_message = (
                                    f"💰 *¡Has recibido un pago!*\n\n"
                                    f"*De:* {from_member_name}\n"
                                    f"*Monto:* ${amount:.2f}\n"
                                    f"*Fecha:* {payment_date}\n\n"
                                    f"Este pago ha sido registrado y actualizado en tu balance familiar."
                                )
                            
                            # Enviar notificación al receptor del pago
                            try:
                                print(f"Intentando enviar notificación a {to_member_name} (ID: {to_telegram_id})")
                                
                                # Intentar convertir el ID a entero si es posible (Telegram espera IDs numéricos)
                                try:
                                    numeric_telegram_id = int(to_telegram_id)
                                    print(f"ID convertido a formato numérico: {numeric_telegram_id}")
                                    to_telegram_id = numeric_telegram_id
                                except (ValueError, TypeError):
                                    print(f"No se pudo convertir el ID a formato numérico, usando el valor original: {to_telegram_id}")
                                
                                # Enviar el mensaje
                                await context.bot.send_message(
                                    chat_id=to_telegram_id,
                                    text=notification_message,
                                    parse_mode="Markdown",
                                    reply_markup=reply_markup
                                )
                                print(f"✅ Notificación enviada exitosamente a {to_member_name} (ID: {to_telegram_id})")
                                
                                # Informar al pagador que la notificación se envió
                                await update.message.reply_text(
                                    f"✅ {to_member_name} ha sido notificado sobre tu pago.",
                                    parse_mode="Markdown"
                                )
                            except Exception as e:
                                error_msg = str(e)
                                print(f"❌ Error al enviar notificación: {error_msg}")
                                
                                # Informar al pagador sobre el problema
                                if "bot was blocked by the user" in error_msg:
                                    await update.message.reply_text(
                                        f"⚠️ No se pudo notificar a {to_member_name} porque ha bloqueado el bot.\n\n" +
                                        f"Para recibir notificaciones, {to_member_name} debe desbloquear el bot y enviar /start.",
                                        parse_mode="Markdown"
                                    )
                                elif "chat not found" in error_msg:
                                    await update.message.reply_text(
                                        f"⚠️ No se pudo notificar a {to_member_name} porque aún no ha iniciado una conversación con el bot.\n\n" + 
                                        f"Para recibir notificaciones, {to_member_name} debe:\n" +
                                        f"1. Buscar @{context.bot.username} en Telegram\n" +
                                        f"2. Iniciar el bot enviando /start",
                                        parse_mode="Markdown"
                                    )
                                else:
                                    await update.message.reply_text(
                                        f"⚠️ No se pudo notificar a {to_member_name} sobre el pago.\n\n" +
                                        f"Error: {error_msg}\n\n" +
                                        f"Es posible que {to_member_name} necesite reiniciar el bot con /start.",
                                        parse_mode="Markdown"
                                    )
                    else:
                        print(f"❌ No se pudo obtener información del receptor: {to_member_id}")
                        await update.message.reply_text(
                            f"⚠️ El pago fue registrado, pero no se pudo notificar al receptor porque no se encontró su información.\n\n" +
                            f"ID del miembro: {to_member_id}\n\n" +
                            f"Posibles soluciones:\n" +
                            f"1. Asegúrate de que el miembro está correctamente registrado en la familia\n" +
                            f"2. Pídele que inicie el bot con /start\n" +
                            f"3. Verifica que su nombre esté correcto en la configuración de la familia",
                            parse_mode="Markdown"
                        )
                
                except Exception as e:
                    print(f"❌ Error general al enviar notificación de pago: {str(e)}")
                    traceback.print_exc()
                    await update.message.reply_text(
                        "⚠️ El pago fue registrado correctamente, pero ocurrió un error al notificar al receptor.",
                        parse_mode="Markdown"
                    )
                
                # Limpiar los datos del pago del contexto
                if "payment_data" in context.user_data:
                    del context.user_data["payment_data"]
                
                return ConversationHandler.END
            else:
                # Manejar específicamente el error de exceso de pago
                error_message = ""
                
                # Extraer el mensaje de error de la respuesta, manejando tanto una estructura plana como anidada
                if isinstance(response_data, dict):
                    # Verificar si el mensaje está directamente en response_data['message']
                    if "message" in response_data:
                        error_message = response_data.get("message", "")
                    # Verificar si el mensaje está anidado en response_data['error']['message']
                    elif "error" in response_data and isinstance(response_data["error"], dict):
                        error_message = response_data["error"].get("message", "")
                    
                    # Verificar si el error menciona que el monto excede la deuda
                    if "excede la deuda actual" in error_message and debt_amount > 0:
                        # Extraer la deuda actual del mensaje para mayor precisión
                        import re
                        debt_matches = re.search(r'\(\$(\d+\.\d+)\)', error_message)
                        if debt_matches:
                            actual_debt = float(debt_matches.group(1))
                            context.user_data["payment_data"]["debt_amount"] = actual_debt
                        
                        # Ofrecer opciones al usuario: ajustar automáticamente o cancelar
                        keyboard = [
                            ["✅ Pagar monto exacto"],  # Ajustar automáticamente al valor correcto
                            ["❌ Cancelar"]             # Cancelar la operación
                        ]
                        
                        await update.message.reply_text(
                            f"⚠️ *Pago Parcial*\n\n"
                            f"El monto del pago (${amount:.2f}) excede la deuda actual (${debt_amount:.2f}).\n\n"
                            f"¿Deseas ajustar el monto automáticamente al valor exacto de la deuda?",
                            parse_mode="Markdown",
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard,
                                one_time_keyboard=True,
                                resize_keyboard=True
                            )
                        )
                        
                        # Permanecer en el estado de confirmación
                        return PAYMENT_CONFIRM
                
                # Si no es un error de exceso de pago o no pudimos manejarlo específicamente,
                # mostrar el error genérico
                if not error_message:
                    error_message = str(response_data)
                
                await send_error(update, context, f"Error al registrar el pago: {error_message}")
                return ConversationHandler.END
        elif response == "❌ Cancelar":
            # Si el usuario cancela, mostrar mensaje
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            
            # Limpiar los datos del pago del contexto
            if "payment_data" in context.user_data:
                del context.user_data["payment_data"]
            
            return ConversationHandler.END
        else:
            # Si la respuesta no es reconocida
            await update.message.reply_text(
                "Opción no reconocida. Por favor, selecciona Confirmar o Cancelar.",
                reply_markup=Keyboards.get_confirmation_keyboard()
            )
            return PAYMENT_CONFIRM
            
    except Exception as e:
        await send_error(update, context, f"Error al confirmar el pago: {str(e)}")
        return ConversationHandler.END
    
async def listar_pagos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra la lista de pagos de la familia.
    
    Esta función recupera todos los pagos de la familia actual y los muestra
    al usuario en un formato ordenado.
    
    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener el ID de Telegram del usuario
        telegram_id = str(update.effective_user.id)
        
        # Enviar mensaje de carga
        message = await update.message.reply_text(
            Messages.LOADING,
            reply_markup=Keyboards.remove_keyboard()
        )
        
        # Obtener el ID de la familia desde el contexto
        family_id = context.user_data.get("family_id")
        
        # Si no tenemos el ID de familia en el contexto, intentar obtenerlo desde la API
        if not family_id:
            status_code, member = MemberService.get_member(telegram_id)
            if status_code == 200 and member and member.get("family_id"):
                family_id = member.get("family_id")
                context.user_data["family_id"] = family_id
            else:
                await message.edit_text(
                    Messages.ERROR_NOT_IN_FAMILY,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return ConversationHandler.END
        
        # Obtener los pagos de la familia
        status_code, payments = PaymentService.get_family_payments(family_id)
        
        # Si hubo un error al obtener los pagos, mostrar mensaje de error
        if status_code != 200 or not payments:
            error_message = payments.get("error", "Error desconocido") if isinstance(payments, dict) else "No se encontraron pagos"
            try:
                await message.edit_text(
                    Messages.ERROR_NO_PAYMENTS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            except Exception as edit_error:
                # Si hay un error al editar el mensaje, enviamos uno nuevo
                await update.message.reply_text(
                    Messages.ERROR_NO_PAYMENTS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            return ConversationHandler.END
        
        # Verificar si hay pagos para mostrar
        if len(payments) == 0:
            try:
                await message.edit_text(
                    Messages.NO_PAYMENTS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            except Exception as edit_error:
                # Si hay un error al editar el mensaje, enviamos uno nuevo
                await update.message.reply_text(
                    Messages.NO_PAYMENTS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            return ConversationHandler.END
        
        # Cargar los nombres de los miembros si no están en el contexto
        member_names = context.user_data.get("member_names", {})
        if not member_names:
            # Cargar los nombres de los miembros desde la API
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
        
        # Construir mensaje con la lista de pagos
        message_text = Messages.PAYMENTS_LIST_HEADER
        
        # Ordenar pagos por fecha (más recientes primero)
        from datetime import datetime
        
        # Intentamos ordenar por fecha si está disponible
        try:
            sorted_payments = sorted(
                payments, 
                key=lambda x: datetime.fromisoformat(x.get("created_at").replace("Z", "+00:00")), 
                reverse=True
            )
        except (AttributeError, ValueError):
            # Si hay un error al ordenar, usar la lista original
            sorted_payments = payments
        
        # Limitar a 10 pagos para no hacer el mensaje demasiado largo
        limited_payments = sorted_payments[:10]
        
        # Construir el mensaje con los pagos
        for payment in limited_payments:
            # Los miembros ahora son objetos completos, no solo IDs
            from_member = payment.get("from_member", {})
            to_member = payment.get("to_member", {})
            
            # Obtener información del miembro que realiza el pago
            from_id = from_member.get("id") if isinstance(from_member, dict) else from_member
            from_name = from_member.get("name") if isinstance(from_member, dict) else member_names.get(str(from_id), f"Usuario {from_id}")
            
            # Obtener información del miembro que recibe el pago
            to_id = to_member.get("id") if isinstance(to_member, dict) else to_member
            to_name = to_member.get("name") if isinstance(to_member, dict) else member_names.get(str(to_id), f"Usuario {to_id}")
            
            amount = payment.get("amount", 0)
            date = payment.get("created_at", "Fecha desconocida")
            
            # Formatear la fecha si es posible
            try:
                date_obj = datetime.fromisoformat(date.replace("Z", "+00:00"))
                formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
            except (ValueError, AttributeError):
                formatted_date = date
            
            # Añadir este pago al mensaje
            message_text += Messages.PAYMENT_LIST_ITEM.format(
                id=payment.get("id", "ID desconocido"),
                from_member=from_name,
                to_member=to_name,
                amount=f"${amount:.2f}",
                date=formatted_date
            )
        
        # Si hay más pagos de los que mostramos, añadir un mensaje indicándolo
        if len(sorted_payments) > 10:
            message_text += f"\n_Mostrando los 10 pagos más recientes de {len(sorted_payments)} en total._"
        
        # Mostrar el mensaje con la lista de pagos
        try:
            await message.edit_text(
                message_text,
                reply_markup=Keyboards.get_main_menu_keyboard(),
                parse_mode="Markdown"
            )
        except Exception as edit_error:
            # Si hay un error al editar el mensaje, enviamos uno nuevo
            await update.message.reply_text(
                message_text,
                reply_markup=Keyboards.get_main_menu_keyboard(),
                parse_mode="Markdown"
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        traceback.print_exc()
        await send_error(update, context, f"Error al mostrar los pagos: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

# Función para forzar la actualización del teclado
async def update_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fuerza la actualización del teclado del menú principal.
    
    Esta función es útil cuando hay problemas de visualización del teclado.
    
    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        await update.message.reply_text(
            "Actualizando teclado...",
            reply_markup=Keyboards.remove_keyboard()
        )
        
        await update.message.reply_text(
            Messages.MAIN_MENU,
            reply_markup=Keyboards.get_main_menu_keyboard()
        )
        
        return ConversationHandler.END
    except Exception as e:
        await send_error(update, context, f"Error al actualizar el teclado: {str(e)}")
        return ConversationHandler.END 