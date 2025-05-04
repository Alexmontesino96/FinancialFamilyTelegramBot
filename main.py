"""
Financial Bot for Telegram - Main Module

This is the main entry point for the Financial Bot application.
The bot allows users to create and manage family finances, track expenses,
register payments, and view balances between family members.
"""

import os
import sys
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
    SELECT_MEMBERS,
    CONFIRM,
    SELECT_TO_MEMBER,
    PAYMENT_AMOUNT,
    PAYMENT_CONFIRM,
    EDIT_OPTION,
    SELECT_EXPENSE,
    SELECT_PAYMENT,
    CONFIRM_DELETE,
    EDIT_EXPENSE_AMOUNT,
    LIST_OPTION,
    SELECT_CREDIT,
    ADJUSTMENT_AMOUNT,
    ADJUSTMENT_CONFIRM,
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
    show_main_menu,
    show_list_options,
    handle_list_option
)
from handlers.expense_handler import (
    get_expense_description,
    get_expense_amount,
    show_expense_division_options,
    select_members_for_expense,
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
    registrar_pago,
    update_keyboard,
    listar_pagos
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
from handlers.adjustment_handler import (
    start_debt_adjustment,
    handle_credit_selection,
    handle_adjustment_amount,
    handle_adjustment_confirmation,
    cancel as adjustment_cancel
)
from handlers.callback_handler import payment_callback_handler
from utils.error_handler import register_error_handlers
from health_check import start_health_check_server

# Importar la función para verificar instancias duplicadas
# Primero intentamos importar el verificador específico para Render
try:
    # Si estamos en Render, usamos el verificador específico
    if os.environ.get('RENDER') == 'true':
        from scripts.render_instance_check import check_render_instance
        has_instance_checker = True
        is_render_checker = True
        logger.info("Usando verificador de instancias específico para Render")
    else:
        # Si no estamos en Render, usamos el verificador genérico
        from scripts.check_bot_instances import check_bot_instances
        has_instance_checker = True
        is_render_checker = False
        logger.info("Usando verificador de instancias genérico")
except ImportError as e:
    logger.warning(f"No se pudo importar el verificador de instancias: {e}. Se omitirá la verificación.")
    has_instance_checker = False
    is_render_checker = False

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
    # Verificar si hay instancias duplicadas del bot
    if has_instance_checker:
        logger.info("Verificando instancias duplicadas del bot...")
        if is_render_checker:
            should_continue = check_render_instance()
        else:
            should_continue = check_bot_instances()
            
        if not should_continue:
            logger.info("Deteniendo esta instancia del bot debido a que ya hay otra instancia en ejecución.")
            sys.exit(0)
    
    # Start health check server if running in production environment (like Render)
    if os.environ.get('RENDER') == 'true':
        logger.info("Running in Render environment, starting health check server")
        health_server = start_health_check_server()
    
    # Crear la aplicación
    logger.info("Starting Financial Bot for Telegram")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register global error handler
    register_error_handlers(application)
    
    # REESTRUCTURACIÓN COMPLETA DE HANDLERS
    
    # Comandos básicos que deben estar siempre disponibles
    application.add_handler(CommandHandler("menu", show_main_menu))
    application.add_handler(CommandHandler("teclado", update_keyboard))
    application.add_handler(CommandHandler("pagos", listar_pagos))
    
    # Crear el manejador para el flujo de creación de familia con alta prioridad
    family_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            ASK_FAMILY_CODE: [
                # Para depuración, registremos el mensaje exacto
                MessageHandler(filters.TEXT & ~filters.COMMAND, 
                               lambda update, context: 
                                   logger.info(f"[DEBUG] Mensaje exacto recibido: '{update.message.text}'") or start_create_family(update, context)),
            ],
            ASK_FAMILY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_user_name)
            ],
            ASK_USER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_family_with_names)
            ],
            JOIN_FAMILY_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, join_family)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        name="family_conversation",
        persistent=False
    )
    
    # Manejadores para otros flujos
    edit_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^✏️ Editar/Eliminar$"), show_edit_options)
        ],
        states={
            EDIT_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_option)],
            SELECT_EXPENSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_select_expense)],
            SELECT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_select_payment)],
            CONFIRM_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm_delete)],
            EDIT_EXPENSE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_expense_amount)]
        },
        fallbacks=[
            CommandHandler("cancel", edit_cancel)
        ],
        name="edit_conversation",
        persistent=False
    )
    
    expense_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💸 Crear Gasto$"), crear_gasto)
        ],
        states={
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expense_description)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expense_amount)],
            SELECT_MEMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_members_for_expense)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_expense)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        name="expense_conversation",
        persistent=False
    )
    
    payment_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💳 Registrar Pago$"), registrar_pago)
        ],
        states={
            SELECT_TO_MEMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_to_member)],
            PAYMENT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_amount)],
            PAYMENT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_payment)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        name="payment_conversation",
        persistent=False
    )
    
    adjustment_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💱 Ajustar Deudas$"), start_debt_adjustment)
        ],
        states={
            SELECT_CREDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_credit_selection)],
            ADJUSTMENT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adjustment_amount)],
            ADJUSTMENT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adjustment_confirmation)]
        },
        fallbacks=[
            CommandHandler("cancel", adjustment_cancel)
        ],
        name="adjustment_conversation",
        persistent=False
    )
    
    list_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📜 Listar Registros$"), show_list_options)
        ],
        states={
            LIST_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_list_option)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        name="list_conversation",
        persistent=False
    )
    
    # Añadir todos los handlers en el orden correcto
    # El orden es importante: desde el más específico hasta el más general
    
    # 1. Los handlers de conversación (manejan flujos específicos)
    application.add_handler(family_conv_handler)
    application.add_handler(edit_conv_handler)
    application.add_handler(expense_conv_handler)
    application.add_handler(payment_conv_handler)
    application.add_handler(adjustment_conv_handler)
    application.add_handler(list_conv_handler)
    
    # 2. Manejador para opciones específicas del menú principal
    application.add_handler(MessageHandler(
        filters.Regex("^(💰 Ver Balances|ℹ️ Info Familia|📋 Ver Gastos|📊 Ver Pagos|🔗 Compartir Invitación|💱 Ajustar Deudas)$"),
        handle_menu_option
    ))
    
    # 2.5 Manejador para callbacks de pagos
    application.add_handler(payment_callback_handler)
    
    # 3. Manejador para texto desconocido (debe ser el último)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_unknown_text
    ))
    
    # Iniciar el bot
    logger.info("Bot is ready to handle updates")
    application.run_polling()
    
if __name__ == "__main__":
    main()