from telegram import Update
from telegram.ext import ContextTypes
from utils import api_request, format_expenses, send_error

async def create_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 4:
        await update.message.reply_text("Uso: /create_expense <family_id> <descripción> <monto> <pagado_por> [member_id1 member_id2 ...]")
        return
    family_id = context.args[0]
    description = context.args[1]
    amount = context.args[2]
    paid_by = context.args[3]
    split_among = context.args[4:] if len(context.args) > 4 else None
    try:
        data = {
            "description": description,
            "amount": float(amount),
            "paid_by": paid_by,
            "split_among": split_among
        }
        response = api_request("POST", "/expenses", data)
        await update.message.reply_text(f"Gasto creado con ID: {response['id']}")
    except Exception as e:
        await send_error(update, context, str(e))

async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todos los gastos de una familia."""
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /list_expenses <family_id>")
        return
    family_id = context.args[0]
    try:
        expenses = api_request("GET", f"/families/{family_id}/expenses")
        formatted = format_expenses(expenses)
        await update.message.reply_text(f"Gastos de la familia {family_id}:\n{formatted}")
    except Exception as e:
        await send_error(update, context, str(e))