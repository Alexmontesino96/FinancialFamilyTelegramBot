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
from utils.error_handler import register_error_handlers
from health_check import start_health_check_server
from languages import get_language_handlers

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
                MessageHandler(filters.TEXT, 
                               lambda update, context: 
                                   logger.info(f"[DEBUG] Mensaje exacto recibido: '{update.message.text}'") or start_create_family(update, context)),
            ],
            ASK_FAMILY_NAME: [
                MessageHandler(filters.TEXT, ask_user_name)
            ],
            ASK_USER_NAME: [
                MessageHandler(filters.TEXT, create_family_with_names)
            ],
            JOIN_FAMILY_CODE: [
                MessageHandler(filters.TEXT, join_family)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^❌ Cancelar$|^❌ Cancel$"), cancel)
        ],
        name="family_conversation",
        persistent=False,
        allow_reentry=True,
        per_chat=True,
        per_user=True
    )
    
    # Manejadores para otros flujos
    edit_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^✏️ Editar/Eliminar$|^✏️ Edit/Delete$"), show_edit_options)
        ],
        states={
            EDIT_OPTION: [MessageHandler(filters.TEXT, handle_edit_option)],
            SELECT_EXPENSE: [MessageHandler(filters.TEXT, handle_select_expense)],
            SELECT_PAYMENT: [MessageHandler(filters.TEXT, handle_select_payment)],
            CONFIRM_DELETE: [MessageHandler(filters.TEXT, handle_confirm_delete)],
            EDIT_EXPENSE_AMOUNT: [MessageHandler(filters.TEXT, handle_edit_expense_amount)]
        },
        fallbacks=[
            CommandHandler("cancel", edit_cancel),
            MessageHandler(filters.Regex("^❌ Cancelar$|^❌ Cancel$"), edit_cancel)
        ],
        name="edit_conversation",
        persistent=False,
        allow_reentry=True,
        per_chat=True,
        per_user=True
    )
    
    expense_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💸 Create Expense$|^💸 Crear Gasto$"), crear_gasto)
        ],
        states={
            DESCRIPTION: [
                MessageHandler(filters.TEXT, get_expense_description)
            ],
            AMOUNT: [
                MessageHandler(filters.TEXT, get_expense_amount)
            ],
            SELECT_MEMBERS: [
                MessageHandler(filters.TEXT, select_members_for_expense)
            ],
            CONFIRM: [
                MessageHandler(filters.TEXT, confirm_expense)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^❌ Cancelar$|^❌ Cancel$"), cancel)
        ],
        name="expense_conversation",
        persistent=False,
        allow_reentry=True,
        per_chat=True,
        per_user=True
    )
    logger.info("Conversation handlers configurados correctamente")
    
    payment_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💳 Registrar Pago$|^💳 Register Payment$"), registrar_pago)
        ],
        states={
            SELECT_TO_MEMBER: [MessageHandler(filters.TEXT, select_to_member)],
            PAYMENT_AMOUNT: [MessageHandler(filters.TEXT, get_payment_amount)],
            PAYMENT_CONFIRM: [MessageHandler(filters.TEXT, confirm_payment)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^❌ Cancelar$|^❌ Cancel$"), cancel)
        ],
        name="payment_conversation",
        persistent=False,
        allow_reentry=True,
        per_chat=True,
        per_user=True
    )
    
    list_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📜 Listar Registros$|^📜 List Records$"), show_list_options)
        ],
        states={
            LIST_OPTION: [MessageHandler(filters.TEXT, handle_list_option)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^❌ Cancelar$|^❌ Cancel$"), cancel)
        ],
        name="list_conversation",
        persistent=False,
        allow_reentry=True,
        per_chat=True,
        per_user=True
    )
    
    # Añadir todos los handlers en el orden correcto
    # El orden es importante: desde el más específico hasta el más general
    
    # 1. Los handlers de conversación (manejan flujos específicos) - Grupo 0 (prioridad máxima)
    application.add_handler(family_conv_handler, group=0)
    application.add_handler(edit_conv_handler, group=0)
    application.add_handler(expense_conv_handler, group=0)
    application.add_handler(payment_conv_handler, group=0)
    application.add_handler(list_conv_handler, group=0)
    
    # Añadir middleware para logging de mensajes
    async def log_message(update, context):
        """Log each message for debugging purposes"""
        if hasattr(update, 'message') and update.message and hasattr(update.message, 'text'):
            message_text = update.message.text
            user_id = update.effective_user.id if update.effective_user else 'Unknown'
            conversation_key = context.chat_data.get('_conversation_key', 'None')
            # Obtener el estado de la conversación desde chat_data
            current_state = "No state found"
            for handler_name in ["expense_conversation", "payment_conversation", "edit_conversation", "list_conversation", "family_conversation", "language_conversation"]:
                if f"{handler_name}_state" in context.chat_data:
                    current_state = f"{handler_name}: {context.chat_data[f'{handler_name}_state']}"
                    break
            
            logger.info(f"[MESSAGE_DEBUG] User: {user_id}, Text: '{message_text}', Conversation: {conversation_key}, State: {current_state}")
        return None
    
    application.add_handler(MessageHandler(filters.ALL, log_message), group=-1)  # group=-1 para que se ejecute primero
    
    # Añadir los manejadores del sistema de idiomas - Grupo 1
    for handler in get_language_handlers():
        application.add_handler(handler, group=1)
    
    # 2. Manejador para opciones específicas del menú principal - Grupo 2 (menor prioridad)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_menu_option
    ), group=2)
    
    # 3. Manejador para texto desconocido (debe ser el último) - Ya no es necesario porque handle_menu_option
    # ahora maneja cualquier texto desconocido internamente

    # Iniciar el bot
    logger.info("Bot is ready to handle updates")
    application.run_polling()
    
if __name__ == "__main__":
    main()