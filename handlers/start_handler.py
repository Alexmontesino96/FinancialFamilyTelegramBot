"""
Start Handler Module

This module handles the initial interaction with the bot, including the welcome message,
family creation, joining existing families, and deep link processing.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import ASK_FAMILY_CODE, ASK_FAMILY_NAME, ASK_USER_NAME, JOIN_FAMILY_CODE
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
    if context.args:  # Si hay argumentos, manejar enlace profundo
        return await handle_deep_link(update, context)
    else:  # Flujo normal de bienvenida
        # Limpiar datos previos para evitar conflictos
        if "family_id" in context.user_data:
            del context.user_data["family_id"]
            
        await update.message.reply_text(
            Messages.WELCOME,
            reply_markup=Keyboards.get_start_keyboard()
        )
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
    option = update.message.text
    
    print(f"Opción seleccionada: {option}")
    
    if option == "🏠 Crear Familia":
        # Iniciamos el flujo de creación de familia
        await update.message.reply_text(
            Messages.CREATE_FAMILY_INTRO,
            reply_markup=Keyboards.remove_keyboard()
        )
        return ASK_FAMILY_NAME
    elif option == "🔗 Unirse a Familia":
        # En lugar de llamar a start_join_family, configuramos el estado directamente
        await update.message.reply_text(
            Messages.JOIN_FAMILY_INTRO,
            reply_markup=Keyboards.remove_keyboard()
        )
        return JOIN_FAMILY_CODE
    else:
        # Si el usuario envía un nombre de familia directamente después de /start,
        # tratarlo como si hubiera elegido "Crear Familia" y usar ese texto como nombre de familia
        
        # Guardar el nombre de familia en el contexto
        context.user_data["family_name"] = option
        
        # Preguntar por el nombre del usuario
        await update.message.reply_text(
            Messages.CREATE_FAMILY_NAME_RECEIVED.format(family_name=option),
            parse_mode="Markdown",
            reply_markup=Keyboards.remove_keyboard()
        )
        
        # Pasar al siguiente estado
        return ASK_USER_NAME

async def ask_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pide el nombre del usuario tras recibir el nombre de la familia."""
    family_name = update.message.text
    context.user_data["family_name"] = family_name
    
    print(f"Nombre de familia recibido: {family_name}")
    
    await update.message.reply_text(
        Messages.CREATE_FAMILY_NAME_RECEIVED.format(family_name=family_name),
        parse_mode="Markdown"
    )
    return ASK_USER_NAME

async def create_family_with_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea la familia con los nombres proporcionados y envía el ID y QR."""
    try:
        user_name = update.message.text
        family_name = context.user_data["family_name"]
        telegram_id = str(update.effective_user.id)
        
        print(f"Creando familia '{family_name}' con usuario '{user_name}' (telegram_id: {telegram_id})")
        
        # Crear la familia con el miembro inicial
        status_code, response = FamilyService.create_family(
            name=family_name,
            members=[{
                "name": user_name,
                "telegram_id": telegram_id
            }]
        )
        
        print(f"Respuesta de create_family: status_code={status_code}, response={response}")
        
        if status_code >= 400:
            error_msg = f"❌ Error al crear la familia. Código de error: {status_code}"
            if isinstance(response, dict) and "detail" in response:
                error_msg += f"\nDetalle: {response['detail']}"
            await update.message.reply_text(error_msg)
            return ConversationHandler.END
        
        # Obtener el ID de la familia creada
        family_id = response.get("id", "")
        print(f"ID de familia obtenido: {family_id}")
        
        if not family_id:
            await update.message.reply_text("❌ Error: No se pudo obtener el ID de la familia creada.")
            return ConversationHandler.END
        
        # Guardar que el usuario está en una familia
        context.user_data["family_id"] = family_id
        print(f"ID de familia guardado en el contexto: {context.user_data['family_id']}")
        
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
        await update.message.reply_text(
            Messages.SUCCESS_FAMILY_CREATED.format(name=family_name, id=family_id),
            parse_mode="Markdown"
        )
        
        # Crear y enviar el código QR
        qr_data = f"https://t.me/{context.bot.username}?start=join_{family_id}"
        qr_image = create_qr_code(qr_data)
        await update.message.reply_photo(
            photo=qr_image,
            caption=Messages.SHARE_INVITATION_QR
        )
        
        # Mostrar el menú principal
        from handlers.menu_handler import show_main_menu
        await show_main_menu(update, context)

    except Exception as e:
        print(f"Error en create_family_with_names: {str(e)}")
        traceback.print_exc()
        await send_error(update, context, str(e))
        # No limpiar el contexto para poder depurar
        # context.user_data.clear()
    
    return ConversationHandler.END

async def start_join_family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo para unirse a una familia."""
    await update.message.reply_text(
        Messages.JOIN_FAMILY_INTRO,
        reply_markup=Keyboards.remove_keyboard(),
        parse_mode="Markdown"
    )
    return JOIN_FAMILY_CODE

async def join_family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el código y une al usuario a la familia."""
    family_id = update.message.text.strip()  # Eliminar espacios en blanco
    
    # Imprimir para depuración
    print(f"Intentando unirse a la familia con ID: {family_id}")
    
    try:
        # Verificar si la familia existe
        status_code, response = FamilyService.get_family(family_id)
        
        # Imprimir para depuración
        print(f"Respuesta de get_family: status_code={status_code}, response={response}")
        
        # Verificar el status code
        if status_code == 404:
            await update.message.reply_text(
                "❌ ID de familia inválido. Por favor, verifica e intenta nuevamente.\n\n"
                "Debes ingresar el ID exacto que te compartieron."
            )
            return JOIN_FAMILY_CODE  # Mantener el estado para permitir otro intento
        elif status_code >= 400:
            await update.message.reply_text(
                f"❌ Error al verificar la familia. Código de error: {status_code}"
            )
            return JOIN_FAMILY_CODE
            
        # Si llegamos aquí, la familia existe
        family_name = response.get("name", "Sin nombre")
        
        # Agregar al usuario a la familia
        telegram_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name
        
        print(f"Añadiendo usuario {telegram_id} ({user_name}) a la familia {family_id}")
        
        status_code, add_response = FamilyService.add_member_to_family(
            family_id=family_id,
            telegram_id=telegram_id,
            name=user_name
        )
        
        # Imprimir para depuración
        print(f"Respuesta de add_member_to_family: status_code={status_code}, response={add_response}")
        
        if status_code >= 400:
            await update.message.reply_text(
                f"❌ Error al unirte a la familia. Código de error: {status_code}"
            )
            return JOIN_FAMILY_CODE
        
        # Guardar el ID de la familia en el contexto
        context.user_data["family_id"] = family_id
        print(f"ID de familia guardado en el contexto: {context.user_data['family_id']}")
        
        # Cargar los miembros de la familia
        success = await ContextManager.load_family_members(context, family_id)
        print(f"Carga de miembros de la familia: {'exitosa' if success else 'fallida'}")
        
        await update.message.reply_text(
            Messages.JOIN_FAMILY_SUCCESS.format(family_name=family_name),
            parse_mode="Markdown"
        )
        
        # Mostrar el menú principal
        from handlers.menu_handler import show_main_menu
        await show_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        print(f"Error al unirse a la familia: {str(e)}")
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