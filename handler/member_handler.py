from telegram import Update
from telegram.ext import ContextTypes
from utils import api_request, send_error

async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Añade un miembro a una familia."""
    if len(context.args) < 3:
        await update.message.reply_text("Uso: /add_member <family_id> <nombre> <teléfono>")
        return
    family_id, name, phone = context.args[0], context.args[1], context.args[2]
    try:
        data = {"name": name, "phone": phone}
        response = api_request("POST", f"/families/{family_id}/members", data)
        await update.message.reply_text(f"Miembro añadido con ID: {response['id']}")
    except Exception as e:
        await send_error(update, context, str(e))

async def get_member_by_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtiene un miembro por su número de teléfono."""
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /get_member_by_phone <teléfono>")
        return
    phone = context.args[0]
    try:
        response = api_request("GET", f"/members/phone/{phone}")
        await update.message.reply_text(
            f"Miembro encontrado: ID: {response['id']}, Nombre: {response['name']}, Teléfono: {response['phone']}"
        )
    except Exception as e:
        await send_error(update, context, str(e))