from telegram import Update
from telegram.ext import ContextTypes
from utils import api_request, send_error

async def make_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Registra un pago entre miembros."""
    if len(context.args) < 3:
        await update.message.reply_text("Uso: /make_payment <from_member> <to_member> <monto>")
        return
    from_member, to_member, amount = context.args[0], context.args[1], context.args[2]
    try:
        data = {
            "from_member": from_member,
            "to_member": to_member,
            "amount": float(amount)
        }
        response = api_request("POST", "/payments", data)
        await update.message.reply_text(f"Pago registrado con ID: {response['id']}")
    except Exception as e:
        await send_error(update, context, str(e))