from telegram import Update
from telegram.ext import ContextTypes
from handler.family_handler import start_create_family
from handler.expense_handler import create_expense, list_expenses
from handler.balance_handler import get_balances
from handler.adjustment_handler import start_adjustment
from handler.payment_handler import make_payment
from utils import get_user_family_id, send_error

async def handle_keyboard_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones del teclado de respuesta."""
    text = update.message.text
    
    if text == "Crear Familia":
        return await start_create_family(update, context)
    
    elif text == "Family Info":
        user_id = update.effective_user.id
        family_id = get_user_family_id(user_id)
        if not family_id:
            await update.message.reply_text("No perteneces a ninguna familia. Usa /create_family para crear una.")
            return
        context.args = [family_id]
        from handler.family_handler import get_family
        return await get_family(update, context)
    
    elif text == "Add Member":
        await update.message.reply_text("Para añadir un miembro, usa el comando /add_member <family_id> <nombre> <teléfono>")
    
    elif text == "Get Member":
        await update.message.reply_text("Para buscar un miembro, usa el comando /get_member_by_phone <teléfono>")
    
    elif text == "Crear Gasto":
        await update.message.reply_text("Para crear un gasto, usa el comando /create_expense <family_id> <descripción> <monto> <pagado_por>")
    
    elif text == "Ver Gastos":
        user_id = update.effective_user.id
        family_id = get_user_family_id(user_id)
        if not family_id:
            await update.message.reply_text("No perteneces a ninguna familia. Usa /create_family para crear una.")
            return
        context.args = [family_id]
        return await list_expenses(update, context)
    
    elif text == "Ajustar Deudas":
        return await start_adjustment(update, context)
    
    elif text == "Ver Balances":
        user_id = update.effective_user.id
        family_id = get_user_family_id(user_id)
        if not family_id:
            await update.message.reply_text("No perteneces a ninguna familia. Usa /create_family para crear una.")
            return
        context.args = [family_id]
        return await get_balances(update, context)
    
    elif text == "Realizar Pago":
        await update.message.reply_text("Para realizar un pago, usa el comando /make_payment <from_member> <to_member> <monto>")
    
    else:
        await update.message.reply_text("Opción no reconocida. Usa /show_menu para ver las opciones disponibles.") 