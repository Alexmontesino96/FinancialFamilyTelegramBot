from telegram import Update
from telegram.ext import ContextTypes
from utils import api_request, format_balances, send_error

async def get_balances(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtiene los balances de una familia."""
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /get_balances <family_id>")
        return
    family_id = context.args[0]
    try:
        balances = api_request("GET", f"/families/{family_id}/balances")
        formatted = format_balances(balances)
        await update.message.reply_text(f"Balances de la familia {family_id}:\n{formatted}")
    except Exception as e:
        await send_error(update, context, str(e))