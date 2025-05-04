from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Definimos una matriz con el texto que aparecerá en cada botón
    # Cada lista interna representa una "fila" de botones
    keyboard = [
        ["Crear Familia", "Family Info"],
        ["Add Member", "Get Member"],
        ["Crear Gasto", "Ver Gastos"],
        ["Ajustar Deudas", "Ver Balances"],
        ["Realizar Pago"]
    ]

    # Creamos la "marca" (markup) del teclado
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,      # Ajusta el tamaño de los botones al ancho de la pantalla
        one_time_keyboard=True     # Opción para que el teclado desaparezca tras un clic
    )

    await update.message.reply_text(
        text="Elige una opción:",
        reply_markup=reply_markup
    )



