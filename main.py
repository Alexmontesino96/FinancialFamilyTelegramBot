from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handler.family_handler import get_family
from handler.family_handler import create_family_conv_handler
from handler.member_handler import add_member, get_member_by_phone
from handler.expense_handler import create_expense, list_expenses
from handler.payment_handler import make_payment
from handler.balance_handler import get_balances
from handler.adjustment_handler import adjustment_conv_handler
from keyboard_handler import handle_keyboard_button
from reply_keyboard import show_menu
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
import os

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Reemplaza con tu token de BotFather
TOKEN = "7739746761:AAFIRUGU9teEe0LIuEU6P9k6if6wl3MCZY0"

async def start(update, context):
    """Comando inicial del bot."""
    await update.message.reply_text(
        "¡Bienvenido al bot de gestión familiar! Usa /help para ver los comandos disponibles."
    )

async def help_command(update, context):
    """Muestra la lista de comandos disponibles."""
    commands = (
        "/create_family <nombre> - Crea una nueva familia\n"
        "/get_family <family_id> - Obtiene detalles de una familia\n"
        "/add_member <family_id> <nombre> <teléfono> - Añade un miembro\n"
        "/get_member_by_phone <teléfono> - Busca un miembro por teléfono\n"
        "/create_expense <family_id> <descripción> <monto> <pagado_por> - Crea un gasto\n"
        "/list_expenses <family_id> - Lista los gastos de una familia\n"
        "/make_payment <from_member> <to_member> <monto> - Registra un pago\n"
        "/get_balances <family_id> - Muestra los balances de la familia\n"
        "/adjust_debt - Ajustar deudas que otros miembros tienen contigo\n"
        "/show_menu - Mostrar menú de opciones"
    )
    await update.message.reply_text(f"Comandos disponibles:\n{commands}")
    

def main():
    """Inicia el bot y registra los manejadores de comandos."""
    application = Application.builder().token(TOKEN).build()

    # Registrar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(create_family_conv_handler)
    application.add_handler(CommandHandler("get_family", get_family))
    application.add_handler(CommandHandler("add_member", add_member))
    application.add_handler(CommandHandler("get_member_by_phone", get_member_by_phone))
    application.add_handler(CommandHandler("create_expense", create_expense))
    application.add_handler(CommandHandler("list_expenses", list_expenses))
    application.add_handler(CommandHandler("make_payment", make_payment))
    application.add_handler(CommandHandler("get_balances", get_balances))
    application.add_handler(CommandHandler("show_menu", show_menu))
    application.add_handler(adjustment_conv_handler)
    
    # Manejador para botones del teclado
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_keyboard_button
    ))

    # Iniciar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
