from telegram import Update
from telegram.ext import ContextTypes, filters
from utils import api_request, format_members, send_error
from create_qr_code import create_qr_code
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
)
from utils import api_request, send_error

# Definir los estados de la conversación
ASK_FAMILY_NAME, ASK_USER_NAME = range(2)

async def start_create_family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia la conversación para crear una familia."""
    await update.message.reply_text(
        "Vamos a crear una nueva familia. Por favor, dime el nombre de la familia.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_FAMILY_NAME

async def ask_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el nombre de la familia y pide el nombre del usuario."""
    context.user_data["family_name"] = update.message.text
    await update.message.reply_text(
        "Gracias. Ahora, por favor, dime el nombre del usuario que crea la familia."
    )
    return ASK_USER_NAME

async def create_family_with_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el nombre del usuario y crea la familia en la API usando solo el nombre de la familia."""
    family_name = context.user_data["family_name"]
    user_name = update.message.text  # Guardamos el nombre, pero no lo usamos en la API
    try:
        # Enviar solo el nombre de la familia a la API
        data = {"name": family_name, "members": [{"telegram_id":str(update.effective_user.id),"name": user_name}]}
        print(data)
        response = api_request("POST", "/families/", data)
        bio = create_qr_code(response['id'])
        await context.bot.send_photo(chat_id=update.effective_chat.id,photo=bio,
        caption="Aquí tienes tu código QR"
    )
        await update.message.reply_text(
            f"Familia '{family_name}' creada con éxito. ID: {response['id']}"
        )
    except Exception as e:
        await send_error(update, context, str(e))
    finally:
        # Limpiar los datos del usuario
        context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación."""
    await update.message.reply_text(
        "Operación cancelada.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# Definir el ConversationHandler
create_family_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("create_family", start_create_family)],
    states={
        ASK_FAMILY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_user_name)],
        ASK_USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_family_with_names)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

async def get_family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtiene detalles de una familia."""
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /get_family <family_id>")
        return
    family_id = context.args[0]
    try:
        print(family_id)
        response = api_request("GET", f"/families/{family_id}")
        members = format_members(response["members"])
        await update.message.reply_text(
            f"Familia: {response['name']} (ID: {response['id']})\nMiembros:\n{members}"
        )
    except Exception as e:
        await send_error(update, context, str(e))