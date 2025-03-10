"""
Financial Bot for Telegram - Main Module

This is the main entry point for the Financial Bot application.
The bot allows users to create and manage family finances, track expenses,
register payments, and view balances between family members.
"""

import os
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ConversationHandler,
    filters
)
from config import (
    BOT_TOKEN, 
    ASK_FAMILY_CODE, 
    ASK_FAMILY_NAME, 
    ASK_USER_NAME, 
    JOIN_FAMILY_CODE,
    DESCRIPTION,
    AMOUNT,
    CONFIRM,
    SELECT_TO_MEMBER,
    PAYMENT_AMOUNT,
    PAYMENT_CONFIRM,
    EDIT_OPTION,
    SELECT_EXPENSE,
    SELECT_PAYMENT,
    CONFIRM_DELETE,
    EDIT_EXPENSE_AMOUNT,
    logger
)
from handlers.start_handler import (
    start, 
    start_create_family, 
    ask_user_name, 
    create_family_with_names,
    join_family,
    start_join_family,
    cancel
)
from handlers.menu_handler import (
    handle_menu_option,
    handle_unknown_text,
    show_main_menu
)
from handlers.expense_handler import (
    get_expense_description,
    get_expense_amount,
    show_expense_confirmation,
    confirm_expense,
    crear_gasto,
    listar_gastos
)
from handlers.payment_handler import (
    select_to_member,
    get_payment_amount,
    show_payment_confirmation,
    confirm_payment,
    registrar_pago
)
from handlers.family_handler import (
    show_balances,
    mostrar_info_familia,
    compartir_invitacion
)
from handlers.edit_handler import (
    show_edit_options,
    handle_edit_option,
    handle_select_expense,
    handle_select_payment,
    handle_confirm_delete,
    handle_edit_expense_amount,
    cancel as edit_cancel
)
from utils.error_handler import register_error_handlers
from health_check import start_health_check_server

def main():
    """
    Main function that initializes and starts the Telegram bot.
    
    This function sets up all the conversation handlers for different flows:
    - Family creation and joining
    - Expense management
    - Payment registration
    - Editing and deleting records
    - Main menu options
    
    The bot uses a conversation-based approach to guide users through different processes.
    """
    # Start health check server if running in production environment (like Render)
    if os.environ.get('RENDER') == 'true':
        logger.info("Running in Render environment, starting health check server")
        health_server = start_health_check_server()
    
    # Crear la aplicación
    logger.info("Starting Financial Bot for Telegram")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register global error handler
    register_error_handlers(application)
    
    # Manejador para el flujo de creación de familia
    family_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            ASK_FAMILY_CODE: [
                MessageHandler(filters.Regex("^🏠 Crear Familia$"), start_create_family),
                MessageHandler(filters.Regex("^🔗 Unirse a Familia$"), start_join_family),
            ],
            ASK_FAMILY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_user_name)],
            ASK_USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_family_with_names)],
            JOIN_FAMILY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, join_family)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(family_handler)
    
    # Manejador para el flujo de edición/eliminación
    edit_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^✏️ Editar/Eliminar$"), show_edit_options),
        ],
        states={
            EDIT_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_option)],
            SELECT_EXPENSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_select_expense)],
            SELECT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_select_payment)],
            CONFIRM_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm_delete)],
            EDIT_EXPENSE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_expense_amount)]
        },
        fallbacks=[CommandHandler("cancel", edit_cancel)]
    )
    application.add_handler(edit_handler)
    
    # Manejador para el flujo de gastos
    expense_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💸 Crear Gasto$"), crear_gasto),
        ],
        states={
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expense_description)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expense_amount)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_expense)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="expense_conversation",
        persistent=False
    )
    application.add_handler(expense_handler)
    
    # Manejador para el flujo de pagos
    payment_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💳 Registrar Pago$"), registrar_pago),
        ],
        states={
            SELECT_TO_MEMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_to_member)],
            PAYMENT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_amount)],
            PAYMENT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_payment)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="payment_conversation",
        persistent=False
    )
    application.add_handler(payment_handler)
    
    # Manejador para opciones del menú principal
    menu_handler = MessageHandler(
        filters.Regex("^(💰 Ver Balances|ℹ️ Info Familia|📋 Ver Gastos|🔗 Compartir Invitación)$"),
        handle_menu_option
    )
    application.add_handler(menu_handler)
    
    # Manejador para texto desconocido (debe ser el último)
    unknown_handler = MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_unknown_text
    )
    application.add_handler(unknown_handler)
    
    # Iniciar el bot
    logger.info("Bot is ready to handle updates")
    application.run_polling()
    
if __name__ == "__main__":
    main()