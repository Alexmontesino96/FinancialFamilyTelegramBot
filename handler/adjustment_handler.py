from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from utils import api_request, send_error, get_user_family_id

# Estados de la conversación
SHOW_CREDITS, SELECT_AMOUNT = range(2)

async def start_adjustment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de ajuste de deudas mostrando los créditos disponibles."""
    user_id = update.effective_user.id
    try:
        # Obtener el ID de la familia del usuario
        family_id = get_user_family_id(user_id)
        if not family_id:
            await update.message.reply_text("No perteneces a ninguna familia. Usa /join_family para unirte a una.")
            return ConversationHandler.END
        
        # Obtener los saldos de la familia
        response = api_request("GET", f"/families/{family_id}/balances")
        
        # Filtrar solo los créditos (donde otras personas deben al usuario)
        credits = []
        for balance in response:
            if balance["to_member"]["telegram_id"] == str(user_id) and balance["amount"] > 0:
                credits.append(balance)
        
        if not credits:
            await update.message.reply_text("No tienes créditos pendientes para ajustar.")
            return ConversationHandler.END
        
        # Guardar los créditos en el contexto
        context.user_data["credits"] = credits
        
        # Crear botones para cada crédito
        keyboard = []
        for credit in credits:
            debtor_name = credit["from_member"]["name"]
            amount = credit["amount"]
            debtor_id = credit["from_member"]["id"]
            button_text = f"{debtor_name} te debe {amount}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"credit_{debtor_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Selecciona el crédito que deseas ajustar:",
            reply_markup=reply_markup
        )
        return SHOW_CREDITS
    except Exception as e:
        await send_error(update, context, str(e))
        return ConversationHandler.END

async def select_credit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección de un crédito y pide el monto a ajustar."""
    query = update.callback_query
    await query.answer()
    
    debtor_id = query.data.split("_")[1]
    context.user_data["selected_debtor_id"] = debtor_id
    
    # Buscar el crédito seleccionado
    credits = context.user_data.get("credits", [])
    selected_credit = next((c for c in credits if c["from_member"]["id"] == debtor_id), None)
    
    if not selected_credit:
        await query.message.reply_text("No se encontró el crédito seleccionado.")
        return ConversationHandler.END
    
    context.user_data["selected_credit"] = selected_credit
    debtor_name = selected_credit["from_member"]["name"]
    amount = selected_credit["amount"]
    
    await query.message.reply_text(
        f"{debtor_name} te debe {amount}. ¿Qué cantidad deseas ajustar de su deuda? "
        f"(Debe ser menor o igual a {amount})"
    )
    return SELECT_AMOUNT

async def process_adjustment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el monto de ajuste y realiza la llamada a la API."""
    try:
        amount_text = update.message.text
        amount = float(amount_text)
        
        selected_credit = context.user_data.get("selected_credit")
        if not selected_credit:
            await update.message.reply_text("Ocurrió un error. Inicia el proceso nuevamente con /adjust_debt")
            return ConversationHandler.END
        
        credit_amount = selected_credit["amount"]
        
        # Validar que el monto no sea mayor que la deuda
        if amount > credit_amount:
            await update.message.reply_text(
                f"El monto a ajustar ({amount}) no puede ser mayor que la deuda actual ({credit_amount}). "
                f"Ingresa un monto válido o cancela con /cancel."
            )
            return SELECT_AMOUNT
        
        # Preparar datos para la API
        data = {
            "from_member": selected_credit["to_member"]["id"],  # El acreedor (usuario actual)
            "to_member": selected_credit["from_member"]["id"],  # El deudor
            "amount": amount
        }
        
        # Llamar al endpoint de ajuste de deuda
        response = api_request(
            "POST", 
            "/payments/debt-adjustment/", 
            data,
            params={"telegram_id": str(update.effective_user.id)}
        )
        
        debtor_name = selected_credit["from_member"]["name"]
        await update.message.reply_text(
            f"Se ha ajustado con éxito {amount} de la deuda de {debtor_name}."
        )
        
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido.")
        return SELECT_AMOUNT
    except Exception as e:
        await send_error(update, context, str(e))
    
    # Limpiar datos de usuario y finalizar conversación
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el proceso de ajuste de deuda."""
    await update.message.reply_text("Proceso de ajuste de deuda cancelado.")
    context.user_data.clear()
    return ConversationHandler.END

# Definir el ConversationHandler
adjustment_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("adjust_debt", start_adjustment)],
    states={
        SHOW_CREDITS: [CallbackQueryHandler(select_credit, pattern=r"^credit_")],
        SELECT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_adjustment)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
) 