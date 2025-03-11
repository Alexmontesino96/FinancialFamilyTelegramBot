"""
Payment Handler Module

This module handles all payment-related operations in the bot, including
registering payments between family members, confirming payments, and
managing payment data throughout the conversation flow.
"""

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import SELECT_TO_MEMBER, PAYMENT_AMOUNT, PAYMENT_CONFIRM
from ui.keyboards import Keyboards
from ui.messages import Messages
from services.payment_service import PaymentService
from services.family_service import FamilyService
from services.member_service import MemberService
from utils.context_manager import ContextManager
from utils.helpers import send_error

# Eliminamos la importación circular
# from handlers.menu_handler import show_main_menu

async def _show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Helper function to show the main menu without circular imports.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    # Importación local para evitar dependencia circular
    from handlers.menu_handler import show_main_menu
    return await show_main_menu(update, context)

async def registrar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the payment registration flow.
    
    This function checks if the user is in a family, retrieves family members,
    and starts the conversation flow for registering a payment to another member.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Limpiar datos previos para evitar conflictos
        if "payment_data" in context.user_data:
            del context.user_data["payment_data"]
        
        # Inicializar estructura de datos para el pago en el contexto
        context.user_data["payment_data"] = {}
        
        # Obtener el ID de Telegram del usuario actual
        telegram_id = str(update.effective_user.id)
        print(f"Buscando miembro con telegram_id: {telegram_id}")
        
        # Verificar si el usuario pertenece a una familia
        status_code, member = MemberService.get_member(telegram_id)
        print(f"Respuesta de get_member: status_code={status_code}, member={member}")
        
        # Si el usuario no está en una familia, mostrar error y terminar
        if status_code != 200 or not member or not member.get("family_id"):
            await update.message.reply_text(
                Messages.ERROR_NOT_IN_FAMILY,
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Obtener el ID de la familia del usuario
        family_id = member.get("family_id")
        print(f"ID de familia obtenido: {family_id}")
        
        # Obtener el ID del miembro que realiza el pago (from_member)
        from_member_id = member.get("id")
        from_member_name = member.get("name", "Tú")
        
        # Guardar datos iniciales en el contexto
        context.user_data["payment_data"]["from_member_id"] = from_member_id
        context.user_data["payment_data"]["from_member_name"] = from_member_name
        context.user_data["payment_data"]["family_id"] = family_id
        context.user_data["payment_data"]["telegram_id"] = telegram_id
        
        # Obtener todos los miembros de la familia para mostrar opciones de pago
        status_code, family = FamilyService.get_family(family_id, telegram_id)
        
        if status_code != 200 or not family:
            # Si hay error al obtener la familia, mostrar mensaje y terminar
            await update.message.reply_text(
                "Error al obtener los miembros de la familia.",
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Obtener la lista de miembros de la familia
        members = family.get("members", [])
        
        # Filtrar para excluir al usuario actual de la lista de destinatarios
        other_members = [m for m in members if m.get("id") != from_member_id]
        
        if not other_members:
            # Si no hay otros miembros, no se puede registrar un pago
            await update.message.reply_text(
                "No hay otros miembros en la familia a quienes puedas registrar un pago.",
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Obtener los balances de la familia para mostrar cuánto debe cada miembro
        status_code, balances = FamilyService.get_family_balances(family_id, telegram_id)
        print(f"Respuesta de get_family_balances: status_code={status_code}, balances={balances}")
        
        # Crear diccionarios para mapear miembros a sus saldos
        balances_dict = {}  # Lo que otros te deben a ti
        debts_dict = {}     # Lo que tú debes a otros
        
        # Crear diccionario de ID a nombres para facilitar referencias
        member_id_to_name = {m.get("id"): m.get("name", "Desconocido") for m in members}
        
        if status_code == 200 and balances:
            print(f"Procesando balances para el miembro {from_member_id} (tipo: {type(from_member_id)})")
            
            # Procesar los balances según su formato
            if isinstance(balances, list) and len(balances) > 0:
                print(f"Formato de balance detectado: tiene {len(balances)} elementos")
                print(f"Primer elemento: {balances[0]}")
                
                # Asegurarnos de que from_member_id se compare de manera consistente
                str_from_member_id = str(from_member_id)
                
                # Revisar el formato de balances
                if isinstance(balances[0], dict) and "member_id" in balances[0]:
                    print("Procesando formato: balances por miembro (con member_id)")
                    # Formato de balances por miembro
                    for balance in balances:
                        balance_member_id = balance.get("member_id")
                        str_balance_member_id = str(balance_member_id) if balance_member_id is not None else None
                        print(f"Comparando member_id: {str_balance_member_id} con from_member_id: {str_from_member_id}")
                        
                        # Si este es el balance del usuario actual
                        if str_balance_member_id == str_from_member_id:
                            print(f"¡Coincidencia encontrada! Procesando balance para {balance_member_id}")
                            # Revisar sus deudas (lo que debe a otros)
                            for debt in balance.get("debts", []):
                                to_id = debt.get("to")
                                amount = debt.get("amount", 0)
                                print(f"  Deuda encontrada: a {to_id} por ${amount:.2f}")
                                if to_id is not None and amount > 0:
                                    # Guardar tanto como string como con el tipo original
                                    debts_dict[to_id] = amount
                                    debts_dict[str(to_id)] = amount
                                    
                            # Revisar sus créditos (lo que otros le deben)
                            for credit in balance.get("credits", []):
                                from_id = credit.get("from")
                                amount = credit.get("amount", 0)
                                print(f"  Crédito encontrado: de {from_id} por ${amount:.2f}")
                                if from_id is not None and amount > 0:
                                    # Guardar tanto como string como con el tipo original
                                    balances_dict[from_id] = amount
                                    balances_dict[str(from_id)] = amount
                                    
                elif isinstance(balances[0], dict) and "from_member" in balances[0] and "to_member" in balances[0]:
                    print("Procesando formato: transacciones pendientes (con from_member y to_member)")
                    # Formato de transacciones pendientes
                    for transaction in balances:
                        from_id = transaction.get("from_member")
                        to_id = transaction.get("to_member")
                        amount = transaction.get("amount", 0)
                        
                        str_from_id = str(from_id) if from_id is not None else None
                        str_to_id = str(to_id) if to_id is not None else None
                        
                        print(f"Transacción: de {str_from_id} a {str_to_id} por ${amount:.2f}")
                        
                        if str_from_id == str_from_member_id:
                            # Tú debes a alguien
                            print(f"  ¡Tú debes a {to_id}!")
                            if to_id is not None and amount > 0:
                                # Guardar tanto como string como con el tipo original
                                debts_dict[to_id] = amount
                                debts_dict[str(to_id)] = amount
                        elif str_to_id == str_from_member_id:
                            # Alguien te debe a ti
                            print(f"  ¡{from_id} te debe a ti!")
                            if from_id is not None and amount > 0:
                                # Guardar tanto como string como con el tipo original
                                balances_dict[from_id] = amount
                                balances_dict[str(from_id)] = amount
                else:
                    print("Procesando formato: antiguo/simplificado")
                    # Formato simplificado (usado en versiones anteriores)
                    for balance in balances:
                        if isinstance(balance, dict):
                            creditor_id = balance.get("creditor_id")
                            debtor_id = balance.get("debtor_id")
                            amount = balance.get("amount", 0)
                            
                            str_creditor_id = str(creditor_id) if creditor_id is not None else None
                            str_debtor_id = str(debtor_id) if debtor_id is not None else None
                            
                            print(f"Balance: creditor={str_creditor_id}, debtor={str_debtor_id}, amount=${amount:.2f}")
                            
                            # Si el usuario actual es acreedor (tiene que recibir dinero)
                            if str_creditor_id == str_from_member_id:
                                print(f"  ¡{debtor_id} te debe a ti!")
                                if debtor_id is not None and amount > 0:
                                    # Guardar tanto como string como con el tipo original
                                    balances_dict[debtor_id] = amount
                                    balances_dict[str(debtor_id)] = amount
                            # Si el usuario actual es deudor (tiene que pagar)
                            elif str_debtor_id == str_from_member_id:
                                print(f"  ¡Tú debes a {creditor_id}!")
                                if creditor_id is not None and amount > 0:
                                    # Guardar tanto como string como con el tipo original
                                    debts_dict[creditor_id] = amount
                                    debts_dict[str(creditor_id)] = amount
        
        # Guardar datos en el contexto
        context.user_data["payment_data"]["members"] = members
        context.user_data["payment_data"]["other_members"] = other_members
        context.user_data["payment_data"]["balances"] = balances_dict
        context.user_data["payment_data"]["debts"] = debts_dict
        
        # Primero mostrar un resumen de tus deudas
        deudas_mensaje = ""
        if debts_dict:
            deudas_lista = []
            for creditor_id, amount in debts_dict.items():
                creditor_name = member_id_to_name.get(creditor_id, f"Usuario {creditor_id}")
                deudas_lista.append(f"• Debes ${amount:.2f} a {creditor_name}")
            deudas_mensaje = "📊 *Resumen de tus deudas:*\n" + "\n".join(deudas_lista) + "\n\n"
        
        # Crear teclado con los nombres de los miembros, destacando a quienes les debes
        member_buttons = []
        print("\n----- DATOS DE MIEMBROS Y SALDOS -----")
        print(f"Total de miembros para mostrar: {len(other_members)}")
        print(f"Balances (lo que te deben): {balances_dict}")
        print(f"Deudas (lo que debes): {debts_dict}")
        
        for member in other_members:
            member_id = member.get("id")
            member_name = member.get("name", "Desconocido")
            
            # Convertir ID a string para comparación consistente
            str_member_id = str(member_id) if member_id is not None else None
            
            # Chequear si le debes dinero a este miembro (buscando por ID original y string)
            debt_amount = debts_dict.get(member_id, debts_dict.get(str_member_id, 0))
            
            # Chequear si te debe dinero este miembro (buscando por ID original y string)
            credit_amount = balances_dict.get(member_id, balances_dict.get(str_member_id, 0))
            
            print(f"Miembro: {member_name} (ID: {member_id}, String ID: {str_member_id})")
            print(f"  - Le debes: ${debt_amount:.2f}")
            print(f"  - Te debe: ${credit_amount:.2f}")
            
            button_text = member_name
            if debt_amount > 0:
                # Si le debes dinero, destacarlo claramente con emojis adicionales
                button_text = f"💸 {member_name} 💸\nDEBES: ${debt_amount:.2f}"
                print(f"  ✅ Botón con deuda: {button_text}")
            elif credit_amount > 0:
                # Si te debe dinero
                button_text = f"💰 {member_name} 💰\nTE DEBE: ${credit_amount:.2f}"
                print(f"  ✅ Botón con crédito: {button_text}")
            else:
                # Incluso sin saldo, mostrar un formato consistente
                button_text = f"{member_name}\nSALDO: $0.00"
                print(f"  ❌ Botón normal: {button_text}")
                
            member_buttons.append([button_text])
        
        print("----- FIN DE DATOS -----\n")
        
        # Agregar botón de cancelar
        member_buttons.append(["❌ Cancelar"])
        
        # Mostrar mensaje para seleccionar el destinatario del pago
        await update.message.reply_text(
            deudas_mensaje + Messages.SELECT_PAYMENT_RECIPIENT,
            reply_markup=ReplyKeyboardMarkup(
                member_buttons, 
                one_time_keyboard=True,
                resize_keyboard=True
            ),
            parse_mode="Markdown"
        )
        
        # Pasar al siguiente estado: seleccionar destinatario
        return SELECT_TO_MEMBER
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en registrar_pago: {str(e)}")
        await send_error(update, context, f"Error al iniciar el registro de pago: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def select_to_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selection of the payment recipient.
    
    This function processes the user's selection of which family member
    will receive the payment and prompts for the payment amount.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el texto completo seleccionado (puede incluir información de saldo)
        selected_text = update.message.text
        
        # Verificar si el usuario canceló la operación
        if selected_text == "❌ Cancelar":
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Recuperar los datos previamente guardados en el contexto
        other_members = context.user_data.get("payment_data", {}).get("other_members", [])
        
        # Extraer solo el nombre del miembro del texto seleccionado
        # El formato puede ser "Nombre\nSALDO: $0.00" o "💸 Nombre 💸\nDEBES: $XX.XX" o "💰 Nombre 💰\nTE DEBE: $XX.XX"
        member_name = selected_text
        
        # Quitar toda la información adicional después del salto de línea
        if "\n" in member_name:
            member_name = member_name.split("\n")[0]
            
        # Quitar emojis si los hay
        if "💸" in member_name or "💰" in member_name:
            member_name = member_name.replace("💸 ", "").replace(" 💸", "").replace("💰 ", "").replace(" 💰", "")
        
        print(f"Nombre extraído: '{member_name}' del texto seleccionado: '{selected_text}'")
        
        # Buscar el miembro seleccionado en la lista de miembros (verificando coincidencia exacta)
        selected_member = None
        for member in other_members:
            if member.get("name") == member_name:
                selected_member = member
                break
                
        # Si no se encontró con coincidencia exacta, intentar una búsqueda más flexible
        if not selected_member:
            print("No se encontró coincidencia exacta, intentando búsqueda flexible...")
            for member in other_members:
                if member.get("name") in member_name or member_name in member.get("name", ""):
                    selected_member = member
                    print(f"Coincidencia flexible encontrada: {member.get('name')}")
                    break
        
        if not selected_member:
            # Si no se encuentra el miembro, mostrar error y volver a pedir
            await update.message.reply_text(
                f"Miembro '{member_name}' no encontrado. Por favor, selecciona un miembro de la lista:",
                reply_markup=ReplyKeyboardMarkup(
                    [[m.get("name", "Desconocido")] for m in other_members] + [["❌ Cancelar"]],
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            return SELECT_TO_MEMBER
        
        # Guardar el ID del miembro destinatario en el contexto
        to_member_id = selected_member.get("id")
        context.user_data["payment_data"]["to_member_id"] = to_member_id
        context.user_data["payment_data"]["to_member_name"] = member_name
        
        # Verificar si hay un balance registrado para este miembro
        balances = context.user_data.get("payment_data", {}).get("balances", {})
        suggested_amount = balances.get(to_member_id, 0)
        
        # Pedir el monto del pago, sugeriendo el monto adeudado si existe
        message_text = Messages.CREATE_PAYMENT_AMOUNT.format(to_member=member_name)
        if suggested_amount > 0:
            message_text += f"\n\n💡 *Sugerencia:* Este miembro te debe ${suggested_amount:.2f}"
        
        await update.message.reply_text(
            message_text,
            parse_mode="Markdown",
            reply_markup=Keyboards.get_cancel_keyboard()
        )
        
        # Pasar al siguiente estado: ingresar monto
        return PAYMENT_AMOUNT
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en select_to_member: {str(e)}")
        await send_error(update, context, f"Error al seleccionar el destinatario: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def get_payment_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the payment amount input from the user.
    
    This function validates and saves the payment amount provided by the user,
    then shows a confirmation message with the payment details.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener el texto del monto ingresado
        amount_text = update.message.text
        
        # Verificar si el usuario canceló la operación
        if amount_text == "❌ Cancelar":
            await update.message.reply_text(
                "Has cancelado el registro de pago.",
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Intentar convertir el texto a un número flotante
        try:
            # Reemplazar comas por puntos para manejar diferentes formatos numéricos
            amount_text = amount_text.replace(',', '.').strip()
            amount = float(amount_text)
            
            # Verificar que el monto sea positivo
            if amount <= 0:
                await update.message.reply_text(
                    "El monto debe ser un número positivo. Por favor, ingresa el monto nuevamente:",
                    reply_markup=Keyboards.get_cancel_keyboard()
                )
                return PAYMENT_AMOUNT
                
        except ValueError:
            # Si no se puede convertir a número, mostrar error
            await update.message.reply_text(
                "El valor ingresado no es un número válido. Por favor, ingresa solo números:",
                reply_markup=Keyboards.get_cancel_keyboard()
            )
            return PAYMENT_AMOUNT
            
        # Guardar el monto validado en el contexto
        context.user_data["payment_data"]["amount"] = amount
        
        # Mostrar la confirmación del pago
        return await show_payment_confirmation(update, context)
        
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en get_payment_amount: {str(e)}")
        await send_error(update, context, f"Error al procesar el monto del pago: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def show_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows a confirmation message with the payment details.
    
    This function displays the payment information for the user to confirm
    before registering it in the database.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Verificar que todos los datos necesarios estén en el contexto
        from_member_id = context.user_data.get("payment_data", {}).get("from_member_id")
        to_member_id = context.user_data.get("payment_data", {}).get("to_member_id")
        from_member_name = context.user_data.get("payment_data", {}).get("from_member_name", "Tú")
        to_member_name = context.user_data.get("payment_data", {}).get("to_member_name")
        amount = context.user_data.get("payment_data", {}).get("amount")
        
        if not all([from_member_id, to_member_id, to_member_name, amount]):
            # Si faltan datos, mostrar error y cancelar
            print(f"Datos incompletos: from_member_id={from_member_id}, to_member_id={to_member_id}, to_member_name={to_member_name}, amount={amount}")
            await update.message.reply_text(
                "Error: Datos incompletos. Por favor, intenta nuevamente.",
                reply_markup=Keyboards.remove_keyboard()
            )
            await _show_menu(update, context)
            return ConversationHandler.END
        
        # Obtener información de deudas
        debts_dict = context.user_data.get("payment_data", {}).get("debts", {})
        debt_amount = debts_dict.get(to_member_id, 0)
        
        # Crear mensaje de confirmación
        confirmation_message = Messages.CREATE_PAYMENT_CONFIRM.format(
            from_member=from_member_name,
            to_member=to_member_name,
            amount=amount
        )
        
        # Añadir información de deuda si existe
        if debt_amount > 0:
            if amount >= debt_amount:
                confirmation_message += f"\n\n✅ Este pago cubrirá tu deuda de ${debt_amount:.2f} con {to_member_name}."
            else:
                remaining = debt_amount - amount
                confirmation_message += f"\n\n⚠️ Este pago cubrirá parcialmente tu deuda de ${debt_amount:.2f} con {to_member_name}.\nQuedarán pendientes ${remaining:.2f}"
        elif debt_amount == 0 and to_member_id in debts_dict:
            confirmation_message += f"\n\n✅ No tienes deudas pendientes con {to_member_name}."
        
        await update.message.reply_text(
            confirmation_message,
            parse_mode="Markdown",
            reply_markup=Keyboards.get_confirmation_keyboard()
        )
        
        # Pasar al siguiente estado: confirmar pago
        return PAYMENT_CONFIRM
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en show_payment_confirmation: {str(e)}")
        await send_error(update, context, f"Error al mostrar la confirmación del pago: {str(e)}")
        await _show_menu(update, context)
        return ConversationHandler.END

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's confirmation response for creating a payment.
    
    This function processes the user's confirmation and creates the payment
    in the database if confirmed, or cancels the operation if rejected.
    
    Args:
        update (Update): Telegram Update object
        context (ContextTypes.DEFAULT_TYPE): Telegram context
        
    Returns:
        int: The next conversation state
    """
    try:
        # Obtener la respuesta del usuario (confirmar o cancelar)
        response = update.message.text.strip()
        
        # Obtener los datos del pago desde el contexto
        payment_data = context.user_data.get("payment_data", {})
        
        # Verificar acciones específicas
        if response == "✅ Confirmar":
            # Si el usuario confirma, obtener datos necesarios para crear el pago
            amount = payment_data.get("amount")
            from_member_id = payment_data.get("from_member_id")
            to_member_id = payment_data.get("to_member_id")
            telegram_id = payment_data.get("telegram_id")
            family_id = payment_data.get("family_id")
            
            # Validar que todos los datos requeridos estén presentes
            if not all([from_member_id, to_member_id, amount]):
                # Si falta algún dato, mostrar error
                await update.message.reply_text(
                    "Faltan datos para crear el pago. Por favor, inténtalo de nuevo.",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                return await _show_menu(update, context)
            
            # Crear el pago a través del servicio
            status_code, response_data = PaymentService.create_payment(
                from_member=from_member_id,
                to_member=to_member_id,
                amount=amount
            )
            
            if status_code in [200, 201]:
                # Si el pago se creó exitosamente, mostrar mensaje de éxito
                await update.message.reply_text(
                    Messages.SUCCESS_PAYMENT_CREATED,
                    parse_mode="Markdown",
                    reply_markup=Keyboards.get_main_menu_keyboard()
                )
                
                # Limpiar los datos del pago del contexto
                if "payment_data" in context.user_data:
                    del context.user_data["payment_data"]
                
                # Volver al menú principal
                return await _show_menu(update, context)
            else:
                # Si hubo un error al crear el pago, mostrar mensaje de error
                error_message = response_data.get("error", "Error desconocido")
                await send_error(update, context, f"Error al registrar el pago: {error_message}")
                return await _show_menu(update, context)
        elif response == "❌ Cancelar":
            # Si el usuario cancela, mostrar mensaje y volver al menú principal
            await update.message.reply_text(
                Messages.CANCEL_OPERATION,
                reply_markup=Keyboards.get_main_menu_keyboard()
            )
            
            # Limpiar los datos del pago del contexto
            if "payment_data" in context.user_data:
                del context.user_data["payment_data"]
            
            # Volver al menú principal
            return await _show_menu(update, context)
        else:
            # Si la respuesta no es reconocida
            await update.message.reply_text(
                "Opción no reconocida. Por favor, selecciona Confirmar o Cancelar.",
                reply_markup=Keyboards.get_confirmation_keyboard()
            )
            return PAYMENT_CONFIRM
            
    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error en confirm_payment: {str(e)}")
        await send_error(update, context, f"Error al confirmar el pago: {str(e)}")
        return await _show_menu(update, context) 