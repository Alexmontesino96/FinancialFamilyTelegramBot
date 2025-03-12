"""
Start Handler Module

This module handles the initial interaction with the bot, including the welcome message,
family creation, joining existing families, and deep link processing.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import ASK_FAMILY_CODE, ASK_FAMILY_NAME, ASK_USER_NAME, JOIN_FAMILY_CODE, logger
from ui.keyboards import Keyboards
from ui.messages import Messages
from services.family_service import FamilyService
from services.member_service import MemberService
from utils.helpers import create_qr_code, parse_deep_link, send_error
from utils.context_manager import ContextManager
import traceback

async def _show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Helper function to show the main menu without circular imports.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    from handlers.menu_handler import show_main_menu
    return await show_main_menu(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initial message with options to create or join a family, or handle deep links.
    
    This function is triggered by the /start command and presents the user with
    options to create a new family or join an existing one. It also handles
    deep links for direct family joining.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "sin username"
    logger.info(f"[START] Usuario {user_id} (@{username}) ha ejecutado el comando /start")
    
    if context.args:  # Si hay argumentos, manejar enlace profundo
        logger.info(f"[START] Usuario {user_id} tiene argumentos: {context.args}")
        return await handle_deep_link(update, context)
    else:  # Flujo normal de bienvenida
        # Limpiar datos previos para evitar conflictos
        if "family_id" in context.user_data:
            old_family_id = context.user_data["family_id"]
            logger.info(f"[START] Eliminando family_id anterior: {old_family_id} del contexto del usuario {user_id}")
            del context.user_data["family_id"]
        
        logger.info(f"[START] Mostrando mensaje de bienvenida y teclado de inicio al usuario {user_id}")
        keyboard = Keyboards.get_start_keyboard()
        logger.debug(f"[START] Botones del teclado de inicio: {keyboard.keyboard}")
            
        await update.message.reply_text(
            Messages.WELCOME,
            reply_markup=keyboard
        )
        
        logger.info(f"[START] Estableciendo estado ASK_FAMILY_CODE para usuario {user_id}")
        return ASK_FAMILY_CODE

async def start_create_family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the flow to create a family or redirects to the join flow.
    
    This function handles the user's choice after the welcome message,
    either starting the family creation process or redirecting to the
    family joining process.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    user_id = update.effective_user.id
    option = update.message.text
    
    logger.info(f"[CREATE_FAMILY] Usuario {user_id} seleccionó opción: '{option}'")
    
    # Comprobar si la opción coincide exactamente con los botones esperados
    if option == "🏠 Crear Familia":
        logger.info(f"[CREATE_FAMILY] Coincidencia exacta con 'Crear Familia' para usuario {user_id}")
    elif option == "🔗 Unirse a Familia":
        logger.info(f"[CREATE_FAMILY] Coincidencia exacta con 'Unirse a Familia' para usuario {user_id}")
    else:
        # Depurar expresiones regulares
        import re
        crear_match = re.search("(?i).*crear.*familia.*|.*🏠.*", option)
        unirse_match = re.search("(?i).*unirse.*familia.*|.*🔗.*", option)
        
        if crear_match:
            logger.info(f"[CREATE_FAMILY] Coincidencia con regex de crear familia: '{option}'")
        elif unirse_match:
            logger.info(f"[CREATE_FAMILY] Coincidencia con regex de unirse a familia: '{option}'")
        else:
            logger.info(f"[CREATE_FAMILY] Sin coincidencia con expresiones regulares: '{option}'")
    
    if option == "🏠 Crear Familia":
        # Si el usuario selecciona crear familia, no es necesario verificar si ya está en una
        # Simplemente iniciamos el flujo de creación
        logger.info(f"[CREATE_FAMILY] Iniciando flujo de creación de familia para usuario {user_id}")
        await update.message.reply_text(
            Messages.CREATE_FAMILY_INTRO,
            reply_markup=Keyboards.remove_keyboard()
        )
        logger.info(f"[CREATE_FAMILY] Estableciendo estado ASK_FAMILY_NAME para usuario {user_id}")
        return ASK_FAMILY_NAME
    elif option == "🔗 Unirse a Familia":
        # En lugar de llamar a start_join_family, configuramos el estado directamente
        logger.info(f"[CREATE_FAMILY] Iniciando flujo para unirse a familia para usuario {user_id}")
        await update.message.reply_text(
            Messages.JOIN_FAMILY_INTRO,
            reply_markup=Keyboards.remove_keyboard()
        )
        logger.info(f"[CREATE_FAMILY] Estableciendo estado JOIN_FAMILY_CODE para usuario {user_id}")
        return JOIN_FAMILY_CODE
    else:
        # Si no es ninguna de las opciones anteriores, asumimos que es una respuesta al ASK_FAMILY_CODE
        # y continuamos con el flujo normal
        logger.info(f"[CREATE_FAMILY] Tratando texto '{option}' como solicitud de crear familia para usuario {user_id}")
        await update.message.reply_text(
            Messages.CREATE_FAMILY_INTRO,
            reply_markup=Keyboards.remove_keyboard()
        )
        logger.info(f"[CREATE_FAMILY] Estableciendo estado ASK_FAMILY_NAME para usuario {user_id}")
        return ASK_FAMILY_NAME

async def ask_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pide el nombre del usuario tras recibir el nombre de la familia."""
    user_id = update.effective_user.id
    family_name = update.message.text
    context.user_data["family_name"] = family_name
    
    logger.info(f"[ASK_USER_NAME] Usuario {user_id} proporcionó nombre de familia: '{family_name}'")
    
    await update.message.reply_text(
        Messages.CREATE_FAMILY_NAME_RECEIVED.format(family_name=family_name),
        parse_mode="Markdown"
    )
    logger.info(f"[ASK_USER_NAME] Estableciendo estado ASK_USER_NAME para usuario {user_id}")
    return ASK_USER_NAME

async def create_family_with_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea la familia con los nombres proporcionados y envía el ID y QR."""
    user_id = update.effective_user.id
    try:
        user_name = update.message.text
        family_name = context.user_data["family_name"]
        telegram_id = str(update.effective_user.id)
        
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] Usuario {user_id} proporcionó su nombre: '{user_name}'")
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] Creando familia '{family_name}' con usuario '{user_name}' (telegram_id: {telegram_id})")
        
        # Crear la familia con el miembro inicial
        status_code, response = FamilyService.create_family(
            name=family_name,
            members=[{
                "name": user_name,
                "telegram_id": telegram_id
            }]
        )
        
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] Respuesta de create_family: status_code={status_code}, response={response}")
        
        if status_code >= 400:
            error_msg = f"❌ Error al crear la familia. Código de error: {status_code}"
            if isinstance(response, dict) and "detail" in response:
                error_msg += f"\nDetalle: {response['detail']}"
            logger.error(f"[CREATE_FAMILY_WITH_NAMES] Error al crear familia: {error_msg}")
            await update.message.reply_text(error_msg)
            return ConversationHandler.END
        
        # Obtener el ID de la familia creada
        family_id = response.get("id", "")
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] ID de familia obtenido: {family_id}")
        
        if not family_id:
            logger.error(f"[CREATE_FAMILY_WITH_NAMES] No se pudo obtener el ID de la familia creada")
            await update.message.reply_text("❌ Error: No se pudo obtener el ID de la familia creada.")
            return ConversationHandler.END
        
        # Guardar que el usuario está en una familia
        context.user_data["family_id"] = family_id
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] ID de familia guardado en el contexto: {context.user_data['family_id']}")
        
        # Guardar la información de la familia directamente en el contexto
        # No es necesario cargar los miembros de la API porque ya sabemos que solo hay uno
        context.user_data["family_info"] = {
            "id": family_id,
            "name": family_name,
            "members": [
                {
                    "id": response.get("member_id", ""),  # Si la API devuelve el ID del miembro
                    "name": user_name,
                    "telegram_id": telegram_id
                }
            ]
        }
        
        # Crear diccionario de nombres de miembros
        member_id = response.get("member_id", "")
        context.user_data["member_names"] = {
            str(member_id): user_name
        }
        
        # Enviar mensaje de éxito con el ID
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] Enviando mensaje de éxito para familia '{family_name}' (ID: {family_id})")
        await update.message.reply_text(
            Messages.SUCCESS_FAMILY_CREATED.format(name=family_name, id=family_id),
            parse_mode="Markdown"
        )
        
        # Crear y enviar el código QR
        qr_data = f"https://t.me/{context.bot.username}?start=join_{family_id}"
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] Generando código QR con URL: {qr_data}")
        qr_image = create_qr_code(qr_data)
        await update.message.reply_photo(
            photo=qr_image,
            caption=Messages.SHARE_INVITATION_QR
        )
        
        # Mostrar el menú principal
        logger.info(f"[CREATE_FAMILY_WITH_NAMES] Mostrando menú principal para usuario {user_id}")
        from handlers.menu_handler import show_main_menu
        await show_main_menu(update, context)

    except Exception as e:
        logger.error(f"[CREATE_FAMILY_WITH_NAMES] Error para usuario {user_id}: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, str(e))
        # No limpiar el contexto para poder depurar
        # context.user_data.clear()
    
    return ConversationHandler.END

async def start_join_family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo para unirse a una familia."""
    user_id = update.effective_user.id
    logger.info(f"[START_JOIN_FAMILY] Usuario {user_id} inicia flujo para unirse a una familia")
    
    await update.message.reply_text(
        Messages.JOIN_FAMILY_INTRO,
        reply_markup=Keyboards.remove_keyboard(),
        parse_mode="Markdown"
    )
    logger.info(f"[START_JOIN_FAMILY] Estableciendo estado JOIN_FAMILY_CODE para usuario {user_id}")
    return JOIN_FAMILY_CODE

async def join_family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el código y une al usuario a la familia."""
    user_id = update.effective_user.id
    family_id = update.message.text.strip()  # Eliminar espacios en blanco
    
    logger.info(f"[JOIN_FAMILY] Usuario {user_id} intenta unirse a la familia con ID: '{family_id}'")
    
    try:
        # Verificar si la familia existe
        logger.info(f"[JOIN_FAMILY] Verificando si existe la familia con ID: {family_id}")
        status_code, response = FamilyService.get_family(family_id)
        
        logger.info(f"[JOIN_FAMILY] Respuesta de get_family: status_code={status_code}, response={response}")
        
        # Verificar el status code
        if status_code == 404:
            logger.warning(f"[JOIN_FAMILY] Familia no encontrada con ID: {family_id}")
            await update.message.reply_text(
                "❌ ID de familia inválido. Por favor, verifica e intenta nuevamente.\n\n"
                "Debes ingresar el ID exacto que te compartieron."
            )
            return JOIN_FAMILY_CODE  # Mantener el estado para permitir otro intento
        elif status_code >= 400:
            logger.error(f"[JOIN_FAMILY] Error al verificar familia: código {status_code}")
            await update.message.reply_text(
                f"❌ Error al verificar la familia. Código de error: {status_code}"
            )
            return JOIN_FAMILY_CODE
            
        # Si llegamos aquí, la familia existe
        family_name = response.get("name", "Sin nombre")
        
        # Agregar al usuario a la familia
        telegram_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name
        
        logger.info(f"[JOIN_FAMILY] Añadiendo usuario {telegram_id} ({user_name}) a la familia {family_id}")
        
        status_code, add_response = FamilyService.add_member_to_family(
            family_id=family_id,
            telegram_id=telegram_id,
            name=user_name
        )
        
        logger.info(f"[JOIN_FAMILY] Respuesta de add_member_to_family: status_code={status_code}, response={add_response}")
        
        if status_code >= 400:
            logger.error(f"[JOIN_FAMILY] Error al unir usuario a familia: código {status_code}")
            await update.message.reply_text(
                f"❌ Error al unirte a la familia. Código de error: {status_code}"
            )
            return JOIN_FAMILY_CODE
        
        # Guardar el ID de la familia en el contexto
        context.user_data["family_id"] = family_id
        logger.info(f"[JOIN_FAMILY] ID de familia guardado en el contexto: {context.user_data['family_id']}")
        
        # Cargar los miembros de la familia
        success = await ContextManager.load_family_members(context, family_id)
        logger.info(f"[JOIN_FAMILY] Carga de miembros de la familia: {'exitosa' if success else 'fallida'}")
        
        await update.message.reply_text(
            Messages.JOIN_FAMILY_SUCCESS.format(family_name=family_name),
            parse_mode="Markdown"
        )
        
        # Mostrar el menú principal
        logger.info(f"[JOIN_FAMILY] Mostrando menú principal para usuario {user_id}")
        from handlers.menu_handler import show_main_menu
        await show_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"[JOIN_FAMILY] Error al unirse a la familia: {str(e)}")
        await send_error(update, context, f"Error al unirse a la familia: {str(e)}")
        return JOIN_FAMILY_CODE  # Mantener el estado para permitir otro intento

async def handle_deep_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja enlaces profundos desde el QR."""
    link_type, value = parse_deep_link(context.args)
    
    if link_type == "join":
        family_id = value
        try:
            # Obtener información del usuario
            telegram_id = str(update.effective_user.id)
            user_name = update.effective_user.first_name
            
            print(f"Procesando enlace de invitación para unirse a la familia {family_id}. Usuario: {user_name} ({telegram_id})")
            
            # Verificar si el usuario ya está en una familia
            status_code, member = MemberService.get_member(telegram_id)
            
            if status_code == 200 and member and member.get("family_id"):
                existing_family_id = member.get("family_id")
                
                # Si ya está en la misma familia, mostrar mensaje informativo
                if existing_family_id == family_id:
                    await update.message.reply_text(
                        f"Ya eres miembro de esta familia. No es necesario unirte de nuevo.",
                        reply_markup=Keyboards.get_main_menu_keyboard()
                    )
                    context.user_data["family_id"] = family_id
                    await ContextManager.load_family_members(context, family_id)
                    return await _show_menu(update, context)
                
                # Si está en otra familia, preguntar si quiere cambiar
                else:
                    await update.message.reply_text(
                        f"Ya perteneces a otra familia. Para unirte a una nueva familia, primero debes salir de la actual.",
                        reply_markup=Keyboards.get_main_menu_keyboard()
                    )
                    context.user_data["family_id"] = existing_family_id
                    await ContextManager.load_family_members(context, existing_family_id)
                    return await _show_menu(update, context)
            
            # Verificar si la familia existe
            status_code, response = FamilyService.get_family(family_id)
            
            if status_code == 404:
                await update.message.reply_text(
                    "❌ La familia a la que intentas unirte no existe. Es posible que haya sido eliminada o que el enlace sea incorrecto.",
                    reply_markup=Keyboards.get_start_keyboard()
                )
                return ASK_FAMILY_CODE
            elif status_code >= 400:
                await update.message.reply_text(
                    f"❌ Error al verificar la familia. Código de error: {status_code}",
                    reply_markup=Keyboards.get_start_keyboard()
                )
                return ASK_FAMILY_CODE
            
            family_name = response.get("name", "Sin nombre")
            
            # Mostrar mensaje de bienvenida
            await update.message.reply_text(
                f"👋 ¡Hola {user_name}! Has sido invitado a unirte a la familia *{family_name}*. Estamos procesando tu solicitud...",
                parse_mode="Markdown"
            )
                
            # Agregar al usuario a la familia
            status_code, add_response = FamilyService.add_member_to_family(
                family_id=family_id,
                telegram_id=telegram_id,
                name=user_name
            )
            
            if status_code >= 400:
                error_message = f"❌ Error al unirte a la familia. Código de error: {status_code}"
                if isinstance(add_response, dict) and "detail" in add_response:
                    error_message += f"\nDetalle: {add_response['detail']}"
                
                await update.message.reply_text(
                    error_message,
                    reply_markup=Keyboards.get_start_keyboard()
                )
                return ASK_FAMILY_CODE

            # Guardar información en el contexto
            context.user_data["family_id"] = family_id
            context.user_data["telegram_id"] = telegram_id
            
            # Mostrar mensaje de éxito
            await update.message.reply_text(
                Messages.JOIN_FAMILY_SUCCESS.format(family_name=family_name),
                parse_mode="Markdown"
            )
            
            # Cargar los miembros de la familia
            await ContextManager.load_family_members(context, family_id)
            
            # Mostrar el menú principal
            return await _show_menu(update, context)
            
        except Exception as e:
            print(f"Error al procesar el enlace de invitación: {str(e)}")
            traceback.print_exc()
            await send_error(update, context, f"Error al procesar la invitación: {str(e)}")
            await update.message.reply_text(
                "Por favor, intenta unirte a la familia manualmente o solicita un nuevo enlace de invitación.",
                reply_markup=Keyboards.get_start_keyboard()
            )
            return ASK_FAMILY_CODE
    else:
        # Si no es un enlace de unirse, mostrar mensaje de bienvenida normal
        await update.message.reply_text(
            Messages.WELCOME,
            reply_markup=Keyboards.get_start_keyboard()
        )
        return ASK_FAMILY_CODE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación."""
    await update.message.reply_text(
        Messages.CANCEL_OPERATION,
        reply_markup=Keyboards.remove_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END 