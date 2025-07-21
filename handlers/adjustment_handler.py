"""
Adjustment Handler Module

Este módulo maneja el flujo de ajuste de deudas en el bot, permitiendo
a los usuarios reducir manualmente las deudas que otros miembros tienen con ellos.
"""

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from ui.keyboards import Keyboards
from ui.messages import Messages
from ui.formatters import Formatters
from services.payment_service import PaymentService
from services.family_service import FamilyService
from services.member_service import MemberService
from utils.context_manager import ContextManager
from utils.helpers import send_error, notify_unknown_username
from config import SELECT_CREDIT, ADJUSTMENT_AMOUNT, ADJUSTMENT_CONFIRM
import traceback

async def start_debt_adjustment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia el flujo de ajuste de deudas.

    Esta función verifica que el usuario esté en una familia, obtiene los balances
    y muestra los créditos pendientes que el usuario puede ajustar.

    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener el ID de Telegram del usuario
        telegram_id = str(update.effective_user.id)
        print(f"[AJUSTE_DEUDAS] ID de Telegram del usuario: {telegram_id}")
        
        # Enviar mensaje de carga
        message = await update.message.reply_text(
            Messages.LOADING,
            reply_markup=Keyboards.remove_keyboard()
        )
        
        # Verificar si el usuario está en una familia
        family_id = context.user_data.get("family_id")
        if not family_id:
            is_in_family = await ContextManager.check_user_in_family(context, telegram_id)
            if not is_in_family:
                try:
                    await message.edit_text(
                        Messages.ERROR_NOT_IN_FAMILY,
                        reply_markup=Keyboards.get_main_menu_keyboard()
                    )
                except Exception as edit_error:
                    print(f"Error al editar mensaje: {str(edit_error)}")
                    await update.message.reply_text(
                        Messages.ERROR_NOT_IN_FAMILY,
                        reply_markup=Keyboards.get_main_menu_keyboard()
                    )
                return ConversationHandler.END
            
            family_id = context.user_data.get("family_id")
        
        print(f"[AJUSTE_DEUDAS] ID de familia: {family_id}")
        
        # Obtener información del miembro actual
        status_code, member = MemberService.get_member(telegram_id)
        print(f"[AJUSTE_DEUDAS] Respuesta get_member: status={status_code}, member={member}")
        
        if status_code != 200 or not member:
            try:
                await message.edit_text(
                    Messages.ERROR_MEMBER_NOT_FOUND,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            except Exception as edit_error:
                print(f"Error al editar mensaje: {str(edit_error)}")
                await update.message.reply_text(
                    Messages.ERROR_MEMBER_NOT_FOUND,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            return ConversationHandler.END
        
        member_id = member.get("id")
        member_name = member.get("name")
        print(f"[AJUSTE_DEUDAS] ID de miembro: {member_id}, Nombre: {member_name}")
        
        # Inicializar datos de ajuste en el contexto
        context.user_data["adjustment_data"] = {
            "member_id": member_id,
            "member_name": member_name
        }
        
        # Obtener los balances de la familia
        status_code, balances = FamilyService.get_family_balances(family_id, telegram_id)
        print(f"[AJUSTE_DEUDAS] Respuesta get_family_balances: status={status_code}, balances={balances}")
        
        if status_code != 200 or not balances:
            try:
                await message.edit_text(
                    "No se pudieron obtener los balances de la familia.",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            except Exception as edit_error:
                print(f"Error al editar mensaje: {str(edit_error)}")
                await update.message.reply_text(
                    "No se pudieron obtener los balances de la familia.",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            return ConversationHandler.END
        
        # Filtrar los créditos (balances donde otros miembros deben al usuario actual)
        credits = []
        
        print(f"[AJUSTE_DEUDAS] Buscando créditos para el miembro con ID: {member_id}")
        for balance in balances:
            from_member = balance.get("from_member", {})
            to_member = balance.get("to_member", {})
            amount = balance.get("amount", 0)
            
            print(f"[AJUSTE_DEUDAS] Verificando balance: from={from_member.get('id')}, to={to_member.get('id')}, amount={amount}")
            
            # Si el usuario actual es el acreedor (to_member) y el monto es positivo
            if to_member.get("id") == member_id and amount > 0:
                from_member_id = from_member.get("id")
                from_member_name = from_member.get("name", f"Usuario {from_member_id}")
                
                print(f"[AJUSTE_DEUDAS] Crédito encontrado: {from_member_name} debe {amount} a {member_name}")
                credits.append((from_member_name, from_member_id, amount))
        
        # Guardar los créditos en el contexto
        context.user_data["adjustment_data"]["credits"] = credits
        print(f"[AJUSTE_DEUDAS] Total de créditos encontrados: {len(credits)}")
        
        # Si no hay créditos, mostrar mensaje y terminar
        if not credits:
            print(f"[AJUSTE_DEUDAS] No se encontraron créditos para el usuario")
            try:
                await message.edit_text(
                    Messages.NO_CREDITS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            except Exception as edit_error:
                print(f"Error al editar mensaje: {str(edit_error)}")
                await update.message.reply_text(
                    Messages.NO_CREDITS,
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
            return ConversationHandler.END
        
        # Mostrar los créditos para seleccionar
        print(f"[AJUSTE_DEUDAS] Mostrando {len(credits)} créditos al usuario")
        try:
            await message.edit_text(
                Messages.DEBT_ADJUSTMENT_INTRO + "\n\n" + Messages.SELECT_CREDIT,
                parse_mode="Markdown",
                reply_markup=Keyboards.get_credits_keyboard(credits)
            )
        except Exception as edit_error:
            print(f"Error al editar mensaje para mostrar créditos: {str(edit_error)}")
            # Si no se puede editar, enviar un nuevo mensaje
            await update.message.reply_text(
                Messages.DEBT_ADJUSTMENT_INTRO + "\n\n" + Messages.SELECT_CREDIT,
                parse_mode="Markdown",
                reply_markup=Keyboards.get_credits_keyboard(credits)
            )
        
        # Guardar la correspondencia entre botones y créditos
        button_map = {}
        for credit in credits:
            from_member_name, from_member_id, amount = credit
            button_text = f"{from_member_name} - ${amount:.2f}"
            button_map[button_text] = (from_member_name, from_member_id, amount)
        
        context.user_data["adjustment_data"]["button_map"] = button_map
        
        return SELECT_CREDIT
        
    except Exception as e:
        print(f"Error en start_debt_adjustment: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al iniciar el ajuste de deudas: {str(e)}")
        return ConversationHandler.END

async def handle_credit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja la selección de un crédito para ajustar.

    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener el texto seleccionado
        selected_text = update.message.text
        
        # Verificar si el usuario canceló
        if selected_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Obtener el crédito seleccionado desde el mapeo de botones
        button_map = context.user_data["adjustment_data"].get("button_map", {})
        selected_credit = button_map.get(selected_text)
        
        if not selected_credit:
            await update.message.reply_text(
                "Crédito no encontrado. Por favor, selecciona un crédito válido.",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Guardar el crédito seleccionado en el contexto
        debtor_name, debtor_id, total_amount = selected_credit
        context.user_data["adjustment_data"]["selected_credit"] = {
            "debtor_name": debtor_name,
            "debtor_id": debtor_id,
            "total_amount": total_amount
        }
        
        # Pedir el monto del ajuste
        await update.message.reply_text(
            Messages.ADJUSTMENT_AMOUNT_PROMPT.format(
                debtor_name=debtor_name,
                total_amount=total_amount
            ),
            parse_mode="Markdown",
            reply_markup=Keyboards.get_cancel_keyboard()
        )
        
        return ADJUSTMENT_AMOUNT
        
    except Exception as e:
        print(f"Error en handle_credit_selection: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al seleccionar el crédito: {str(e)}")
        return ConversationHandler.END

async def handle_adjustment_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja el ingreso del monto de ajuste.

    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener el texto ingresado
        amount_text = update.message.text
        
        # Verificar si el usuario canceló
        if amount_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Intentar convertir el monto a número
        try:
            # Reemplazar comas por puntos para manejar diferentes formatos numéricos
            amount_text = amount_text.replace(',', '.').strip()
            amount = float(amount_text)
            
            # Verificar que el monto sea positivo
            if amount <= 0:
                await update.message.reply_text(
                    Messages.INVALID_ADJUSTMENT_AMOUNT,
                    reply_markup=Keyboards.get_cancel_keyboard()
                )
                return ADJUSTMENT_AMOUNT
                
        except ValueError:
            await update.message.reply_text(
                Messages.INVALID_ADJUSTMENT_AMOUNT,
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return ADJUSTMENT_AMOUNT
        
        # Obtener el crédito seleccionado del contexto
        selected_credit = context.user_data["adjustment_data"].get("selected_credit", {})
        total_amount = selected_credit.get("total_amount", 0)
        
        # Verificar que el monto no exceda la deuda total
        if amount > total_amount:
            await update.message.reply_text(
                Messages.ADJUSTMENT_AMOUNT_TOO_HIGH.format(
                    amount=amount,
                    total=total_amount
                ),
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return ADJUSTMENT_AMOUNT
        
        # Guardar el monto en el contexto
        context.user_data["adjustment_data"]["amount"] = amount
        
        # Pedir confirmación del ajuste
        debtor_name = selected_credit.get("debtor_name", "")
        creditor_name = context.user_data["adjustment_data"].get("member_name", "")
        
        await update.message.reply_text(
            Messages.ADJUSTMENT_CONFIRM.format(
                debtor_name=debtor_name,
                creditor_name=creditor_name,
                amount=amount
            ),
            parse_mode="Markdown",
            reply_markup=Keyboards.get_confirmation_keyboard()
        )
        
        return ADJUSTMENT_CONFIRM
        
    except Exception as e:
        print(f"Error en handle_adjustment_amount: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al procesar el monto de ajuste: {str(e)}")
        return ConversationHandler.END

async def handle_adjustment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja la confirmación del ajuste de deuda.

    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    try:
        # Obtener la respuesta
        response = update.message.text
        
        # Verificar si el usuario confirmó
        if response != "✅ Confirmar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Obtener los datos necesarios del contexto
        adjustment_data = context.user_data.get("adjustment_data", {})
        selected_credit = adjustment_data.get("selected_credit", {})
        
        debtor_id = selected_credit.get("debtor_id")
        creditor_id = adjustment_data.get("member_id")
        amount = adjustment_data.get("amount")
        
        telegram_id = str(update.effective_user.id)
        
        # Realizar el ajuste de deuda a través del servicio
        status_code, response = PaymentService.create_debt_adjustment(
            from_member=debtor_id,
            to_member=creditor_id,
            amount=amount,
            telegram_id=telegram_id
        )
        
        # Manejar la respuesta
        if status_code in [200, 201]:
            await update.message.reply_text(
                Messages.ADJUSTMENT_SUCCESS,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
        else:
            error_message = response.get("error", "Error desconocido")
            await update.message.reply_text(
                f"Error al ajustar la deuda: {error_message}",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        print(f"Error en handle_adjustment_confirmation: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, f"Error al confirmar el ajuste: {str(e)}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancela el flujo de ajuste de deudas.

    Args:
        update (Update): Objeto Update de Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto de Telegram
        
    Returns:
        int: El siguiente estado de la conversación
    """
    # Limpiar datos de ajuste del contexto
    if "adjustment_data" in context.user_data:
        del context.user_data["adjustment_data"]
    
    # Mostrar mensaje de cancelación
    await update.message.reply_text(
        Messages.OPERATION_CANCELED,
        reply_markup=Keyboards.get_main_menu_keyboard()
    )
    
    # Terminar la conversación
    return ConversationHandler.END 