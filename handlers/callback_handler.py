"""
Módulo para manejar callbacks de botones inline, especialmente para confirmaciones de pagos.

Este módulo contiene funciones para procesar los callbacks generados cuando un usuario
interactúa con botones inline en mensajes, como confirmaciones de pagos.
"""

import json
import logging
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from services.payment_service import PaymentService
from services.member_service import MemberService
from datetime import datetime

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_payment_callback(update: Update, context: CallbackContext):
    """
    Maneja los callbacks relacionados con pagos (confirmar/rechazar).
    
    Esta función procesa las interacciones con los botones inline para confirmaciones
    de pagos, actualizando el estado del pago según la acción del usuario.
    
    Args:
        update (Update): El objeto Update de Telegram
        context (CallbackContext): El contexto de la conversación
    """
    query = update.callback_query
    
    try:
        # Extraer los datos del callback
        callback_data = json.loads(query.data)
        
        # Verificar que sea un callback de tipo 'payment'
        if callback_data.get("type") != "payment":
            await query.answer("Tipo de callback no reconocido")
            return
        
        # Obtener la acción y el ID del pago
        action = callback_data.get("action")
        payment_id = callback_data.get("payment_id")
        
        if not payment_id:
            await query.answer("ID de pago no encontrado en el callback")
            return
        
        # Obtener el ID de Telegram del usuario que confirmará
        telegram_id = update.effective_user.id
        
        # Verificar que el usuario que confirma no sea el mismo que creó el pago
        status_code, payment_data = PaymentService.get_payment(payment_id)
        
        if status_code != 200 or not payment_data:
            await query.answer("No se pudo obtener información del pago")
            return
        
        # Extraer información relevante del pago
        from_member_id = payment_data.get("from_member")
        to_member_id = payment_data.get("to_member")
        amount = payment_data.get("amount", 0)
        current_status = payment_data.get("status", "PENDING")
        
        # Verificar si el pago ya fue procesado
        if current_status != "PENDING":
            if current_status == "CONFIRM":
                await query.answer("Este pago ya ha sido confirmado")
            elif current_status == "REJECT":
                await query.answer("Este pago ya ha sido rechazado")
            else:
                await query.answer(f"Este pago tiene un estado no válido para cambios: {current_status}")
            return
        
        # Verificar que quien confirma es el destinatario del pago
        status_code, to_member_data = MemberService.get_member_by_id(to_member_id)
        
        if status_code != 200 or not to_member_data:
            await query.answer("No se pudo verificar el destinatario del pago")
            return
        
        # Verificar si el ID de Telegram del destinatario coincide con quien confirma
        to_member_telegram_id = to_member_data.get("telegram_id")
        
        if str(to_member_telegram_id) != str(telegram_id):
            await query.answer("Solo el destinatario del pago puede confirmar o rechazar este pago")
            return
        
        # Procesar la acción (confirmar o rechazar)
        if action == "confirm":
            # Confirmar el pago
            status_code, result = PaymentService.confirm_payment(payment_id, telegram_id)
            
            if status_code == 200:
                # Obtener datos del pagador para mostrar en la confirmación
                status_code, from_member_data = MemberService.get_member_by_id(from_member_id)
                from_member_name = from_member_data.get("name", "Usuario") if status_code == 200 else "Usuario"
                
                # Formatear la fecha actual
                payment_date = payment_data.get("created_at")
                if isinstance(payment_date, str) and "T" in payment_date:
                    payment_date = payment_date.split("T")[0].replace("-", "/")
                else:
                    payment_date = datetime.now().strftime("%d/%m/%Y")
                
                # Actualizar el mensaje con la confirmación
                await query.edit_message_text(
                    text=(
                        f"✅ *¡Pago confirmado!*\n\n"
                        f"*De:* {from_member_name}\n"
                        f"*Monto:* ${amount:.2f}\n"
                        f"*Fecha:* {payment_date}\n\n"
                        f"Has confirmado este pago y ha sido aplicado a tu balance."
                    ),
                    parse_mode="Markdown"
                )
                
                await query.answer("Pago confirmado exitosamente")
                
                # Intentar notificar al pagador que su pago fue confirmado
                try:
                    if from_member_data and "telegram_id" in from_member_data:
                        from_telegram_id = from_member_data.get("telegram_id")
                        
                        # Obtener nombre del destinatario
                        to_member_name = to_member_data.get("name", "Usuario")
                        
                        # Enviar notificación al pagador
                        await context.bot.send_message(
                            chat_id=from_telegram_id,
                            text=(
                                f"✅ *Tu pago ha sido confirmado*\n\n"
                                f"*Destinatario:* {to_member_name}\n"
                                f"*Monto:* ${amount:.2f}\n"
                                f"*Fecha:* {payment_date}\n\n"
                                f"{to_member_name} ha confirmado tu pago y ha sido aplicado al balance."
                            ),
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logger.error(f"Error al notificar confirmación al pagador: {str(e)}")
                    # Si falla, continuamos sin mostrar error al usuario
            else:
                # Si hay error al confirmar
                error_message = "No se pudo confirmar el pago"
                if isinstance(result, dict) and "message" in result:
                    error_message = result.get("message")
                
                await query.answer(f"Error: {error_message}")
                
                # Actualizar mensaje con error
                await query.edit_message_text(
                    text=(
                        f"❌ *Error al confirmar el pago*\n\n"
                        f"No se pudo procesar la confirmación: {error_message}\n\n"
                        f"Por favor, contacta al administrador de la aplicación."
                    ),
                    parse_mode="Markdown"
                )
                
        elif action == "reject":
            # Rechazar el pago
            status_code, result = PaymentService.update_payment_status(payment_id, "REJECT", telegram_id)
            
            if status_code == 200:
                # Obtener datos del pagador para mostrar en la confirmación
                status_code, from_member_data = MemberService.get_member_by_id(from_member_id)
                from_member_name = from_member_data.get("name", "Usuario") if status_code == 200 else "Usuario"
                
                # Formatear la fecha actual
                payment_date = payment_data.get("created_at")
                if isinstance(payment_date, str) and "T" in payment_date:
                    payment_date = payment_date.split("T")[0].replace("-", "/")
                else:
                    payment_date = datetime.now().strftime("%d/%m/%Y")
                
                # Actualizar el mensaje con el rechazo
                await query.edit_message_text(
                    text=(
                        f"❌ *Pago rechazado*\n\n"
                        f"*De:* {from_member_name}\n"
                        f"*Monto:* ${amount:.2f}\n"
                        f"*Fecha:* {payment_date}\n\n"
                        f"Has rechazado este pago. No se aplicarán cambios a tu balance."
                    ),
                    parse_mode="Markdown"
                )
                
                await query.answer("Pago rechazado")
                
                # Intentar notificar al pagador que su pago fue rechazado
                try:
                    if from_member_data and "telegram_id" in from_member_data:
                        from_telegram_id = from_member_data.get("telegram_id")
                        
                        # Obtener nombre del destinatario
                        to_member_name = to_member_data.get("name", "Usuario")
                        
                        # Enviar notificación al pagador
                        await context.bot.send_message(
                            chat_id=from_telegram_id,
                            text=(
                                f"❌ *Tu pago ha sido rechazado*\n\n"
                                f"*Destinatario:* {to_member_name}\n"
                                f"*Monto:* ${amount:.2f}\n"
                                f"*Fecha:* {payment_date}\n\n"
                                f"{to_member_name} ha rechazado tu pago. No se han aplicado cambios al balance."
                            ),
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logger.error(f"Error al notificar rechazo al pagador: {str(e)}")
                    # Si falla, continuamos sin mostrar error al usuario
            else:
                # Si hay error al rechazar
                error_message = "No se pudo rechazar el pago"
                if isinstance(result, dict) and "message" in result:
                    error_message = result.get("message")
                
                await query.answer(f"Error: {error_message}")
                
                # Actualizar mensaje con error
                await query.edit_message_text(
                    text=(
                        f"❌ *Error al rechazar el pago*\n\n"
                        f"No se pudo procesar el rechazo: {error_message}\n\n"
                        f"Por favor, contacta al administrador de la aplicación."
                    ),
                    parse_mode="Markdown"
                )
        else:
            await query.answer(f"Acción no reconocida: {action}")
            
    except json.JSONDecodeError:
        await query.answer("Error al decodificar datos del callback")
        logger.error(f"Error al decodificar JSON del callback: {query.data}")
    except Exception as e:
        await query.answer("Ocurrió un error al procesar la acción")
        logger.error(f"Error en handle_payment_callback: {str(e)}", exc_info=True)

# Crear el manejador de callbacks para pagos
payment_callback_handler = CallbackQueryHandler(
    handle_payment_callback,
    pattern=r'^{"type":"payment"'
) 