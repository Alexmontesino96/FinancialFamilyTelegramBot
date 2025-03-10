"""
Error Handler Module

This module provides global error handling functionality for the bot.
It ensures that the application continues running even when unexpected errors occur.
"""

import html
import json
import traceback
import os
from telegram import Update
from telegram.ext import ContextTypes, Application
from telegram.constants import ParseMode
from config import logger

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global error handler for the bot.
    
    This function catches all unhandled exceptions in the bot and logs them.
    It also sends a message to the user if possible, informing them that an error occurred.
    
    Args:
        update (object): The update that caused the error
        context (ContextTypes.DEFAULT_TYPE): The context that caused the error
    """
    # Log the error
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Extract error information
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    
    # Log the traceback
    logger.error(f"Traceback: {tb_string}")
    
    # Prepare error message
    error_message = f"An unexpected error occurred: {context.error}"
    
    # Send message to the user if possible
    if update and hasattr(update, 'effective_message') and update.effective_message:
        # Send a message to the user
        await update.effective_message.reply_text(
            "Lo sentimos, ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."
        )
    
    # If we have admin chat ID, send detailed error information there
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    if admin_chat_id:
        try:
            # Format update info if available
            update_str = ""
            if update:
                update_str = json.dumps(update.to_dict(), indent=2, ensure_ascii=False)
                if len(update_str) > 1000:  # Truncate if too long
                    update_str = update_str[:1000] + "..."
            
            # Send detailed error message to admin
            error_text = (
                f"⚠️ <b>Error en el bot</b>\n\n"
                f"<b>Error:</b> {html.escape(str(context.error))}\n\n"
                f"<b>Traceback:</b>\n<pre>{html.escape(tb_string[:2000] if len(tb_string) > 2000 else tb_string)}</pre>\n\n"
            )
            
            # Add update info if available
            if update_str:
                error_text += f"<b>Update:</b>\n<pre>{html.escape(update_str)}</pre>"
            
            # Send message in chunks if needed
            if len(error_text) > 4000:
                # Split into chunks of 4000 characters
                for i in range(0, len(error_text), 4000):
                    chunk = error_text[i:i+4000]
                    await context.bot.send_message(
                        chat_id=admin_chat_id,
                        text=chunk,
                        parse_mode=ParseMode.HTML
                    )
            else:
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=error_text,
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"Failed to send error message to admin: {e}")

def register_error_handlers(application: Application) -> None:
    """
    Registers the error handler with the application.
    
    Args:
        application (Application): The telegram bot application
    """
    application.add_error_handler(error_handler)
    logger.info("Error handler registered") 