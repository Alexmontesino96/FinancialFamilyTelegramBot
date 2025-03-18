"""
Mensajes en Español

Este archivo contiene todos los textos mostrados por el bot en español.
"""

class Messages:
    """Mensajes formateados para Telegram en Español."""
    
    # Mensajes de bienvenida
    WELCOME = (
        "👋 ¡Bienvenido al Bot de Gestión Familiar!\n"
        "Este bot te ayuda a gestionar gastos compartidos con tu familia o grupo de amigos.\n"
        "¿Qué deseas hacer?"
    )
    
    MAIN_MENU = "✨ ¡Bienvenido a tu panel familiar!\nSelecciona una opción:"
    
    # Mensajes de error
    ERROR_NOT_IN_FAMILY = "❌ No estás en ninguna familia. Usa /start para crear o unirte a una familia."
    ERROR_FAMILY_NOT_FOUND = "❌ Familia no encontrada. Puede que haya sido eliminada."
    ERROR_INVALID_OPTION = "❌ Opción no válida. Por favor, selecciona una opción del menú."
    ERROR_API = "❌ Error de comunicación con la API. Por favor, inténtalo de nuevo más tarde."
    ERROR_INVALID_AMOUNT = "❌ Monto no válido. Por favor, introduce un número positivo."
    ERROR_CREATING_EXPENSE = "❌ Error al crear el gasto. Por favor, inténtalo de nuevo más tarde."
    ERROR_MEMBER_NOT_FOUND = "❌ No se encontró tu información de miembro. Por favor, inténtalo de nuevo."
    ERROR_NO_EXPENSES = "❌ No hay gastos registrados para mostrar."
    ERROR_NO_PAYMENTS = "❌ No hay pagos registrados para mostrar."
    ERROR_EXPENSE_NOT_FOUND = "❌ No se encontró el gasto especificado."
    ERROR_PAYMENT_NOT_FOUND = "❌ No se encontró el pago especificado."
    ERROR_DELETING_EXPENSE = "❌ Error al eliminar el gasto. Por favor, inténtalo de nuevo más tarde."
    ERROR_DELETING_PAYMENT = "❌ Error al eliminar el pago. Por favor, inténtalo de nuevo más tarde."
    ERROR_UPDATING_EXPENSE = "❌ Error al actualizar el gasto. Por favor, inténtalo de nuevo más tarde."
    
    # Mensajes de éxito
    SUCCESS_FAMILY_CREATED = "✅ Familia '{name}' creada con éxito.\n*ID:* `{id}`"
    SUCCESS_JOINED_FAMILY = "🎉 ¡Te has unido a la familia *{family_name}* con éxito!"
    SUCCESS_EXPENSE_CREATED = "✅ ¡Gasto creado con éxito!"
    SUCCESS_PAYMENT_CREATED = "✅ ¡Pago registrado con éxito!"
    SUCCESS_EXPENSE_DELETED = "✅ Gasto eliminado con éxito."
    SUCCESS_PAYMENT_DELETED = "✅ Pago eliminado con éxito."
    SUCCESS_EXPENSE_UPDATED = "✅ Gasto actualizado con éxito."
    
    # Mensajes de flujo de creación de familia
    CREATE_FAMILY_INTRO = "🏠 Vamos a crear una nueva familia.\n\n" \
                         "¿Cómo se llamará tu familia?"
    
    CREATE_FAMILY_NAME_RECEIVED = "👍 Nombre de familia recibido: *{family_name}*\n\n" \
                                 "Ahora, ¿cuál es tu nombre? Así te identificarán los demás miembros."
    
    # Mensajes de flujo para unirse a una familia
    JOIN_FAMILY_INTRO = "🔗 Vamos a unirte a una familia existente.\n\n" \
                       "Por favor, introduce el ID de la familia a la que deseas unirte:"
    
    JOIN_FAMILY_NAME_PROMPT = "👍 Código de familia válido.\n\n" \
                             "¿Cuál es tu nombre? Así te identificarán los demás miembros."
    
    JOIN_FAMILY_SUCCESS = "✅ ¡Te has unido a la familia *{family_name}* con éxito!"
    
    # Mensajes de flujo de gastos
    CREATE_EXPENSE_INTRO = "💸 Vamos a crear un nuevo gasto.\n\n" \
                          "¿Cuál es la descripción del gasto? (Ej: Supermercado, Cena, etc.)"
    
    CREATE_EXPENSE_AMOUNT = "👍 Descripción recibida: *{description}*\n\n" \
                           "Ahora, ¿cuál es el monto del gasto? (Ej: 100.50)"
    
    CREATE_EXPENSE_DIVISION = "👍 Monto recibido: *${amount:.2f}*\n\n" \
                             "¿Cómo quieres dividir este gasto?"
    
    CREATE_EXPENSE_SELECT_MEMBERS = "👥 Selecciona los miembros que compartirán este gasto:\n\n" \
                                   "Presiona un nombre para seleccionar/deseleccionar\n" \
                                   "- Los nombres con ✅ están seleccionados\n" \
                                   "- Los nombres con ⬜ no están seleccionados\n\n" \
                                   "Cuando hayas terminado, presiona \"✓ Continuar\""
    
    CREATE_EXPENSE_CONFIRM = "📝 Resumen del gasto:\n\n" \
                            "*Descripción:* {description}\n" \
                            "*Monto:* ${amount:.2f}\n" \
                            "*Pagado por:* {paid_by}\n" \
                            "*Compartido entre:* {split_among}\n\n" \
                            "¿Confirmas este gasto?"
    
    # Mensajes para listar gastos
    EXPENSES_LIST_HEADER = "📋 *Lista de Gastos*\n\n"
    
    EXPENSE_LIST_ITEM = (
        "*Descripción:* {description}\n"
        "*Monto:* {amount}\n"
        "*Pagado por:* {paid_by}\n"
        "*Fecha:* {date}\n"
        "----------------------------\n\n"
    )
    
    # Mensajes para listar pagos
    PAYMENTS_LIST_HEADER = "💳 *Lista de Pagos*\n\n"
    
    PAYMENT_LIST_ITEM = (
        "*De:* {from_member}\n"
        "*Para:* {to_member}\n"
        "*Monto:* {amount}\n"
        "*Fecha:* {date}\n"
        "----------------------------\n\n"
    )
    
    # Mensajes para gastos y pagos no encontrados
    NO_EXPENSES = "📋 No hay gastos registrados en esta familia."
    NO_PAYMENTS = "💳 No hay pagos registrados en esta familia."
    
    # Mensajes de flujo de pagos
    CREATE_PAYMENT_INTRO = "💳 Vamos a registrar un nuevo pago.\n\n" \
                          "¿A quién le estás pagando?"
    
    NO_DEBTS = "✅ *¡Felicidades!* En este momento no tienes deudas pendientes con ningún miembro de tu familia."
    
    SELECT_PAYMENT_RECIPIENT = "💳 ¿A quién deseas pagarle? Selecciona un miembro de tu familia a quien le debas dinero:"
    
    CREATE_PAYMENT_AMOUNT = "👍 Destinatario seleccionado: *{to_member}*\n\n" \
                           "Ahora, ¿cuál es el monto del pago? (Ej: 100.50)"
    
    CREATE_PAYMENT_CONFIRM = "📝 Resumen del pago:\n\n" \
                            "*De:* {from_member}\n" \
                            "*Para:* {to_member}\n" \
                            "*Monto:* ${amount:.2f}\n\n" \
                            "¿Confirmas este pago?"
    
    # Mensajes de edición/eliminación
    EDIT_OPTIONS = "✏️ ¿Qué deseas hacer?"
    
    SELECT_EXPENSE_TO_EDIT = "📝 Selecciona el gasto que deseas editar:"
    SELECT_EXPENSE_TO_DELETE = "🗑️ Selecciona el gasto que deseas eliminar:"
    
    SELECT_PAYMENT_TO_EDIT = "📝 Selecciona el pago que deseas editar:"
    SELECT_PAYMENT_TO_DELETE = "🗑️ Selecciona el pago que deseas eliminar:"
    
    CONFIRM_DELETE_EXPENSE = "⚠️ ¿Estás seguro de que deseas eliminar este gasto?\n\n{details}"
    CONFIRM_DELETE_PAYMENT = "⚠️ ¿Estás seguro de que deseas eliminar este pago?\n\n{details}"
    
    EDIT_EXPENSE_AMOUNT = "📝 Ingresa el nuevo monto para el gasto:\n\n{details}"
    
    # Mensajes adicionales para edición/eliminación
    INVALID_EDIT_OPTION = "❌ Opción de edición no válida. Por favor, selecciona una opción del menú."
    NO_EXPENSES_TO_EDIT = "❌ No hay gastos registrados para editar."
    NO_EXPENSES_TO_DELETE = "❌ No hay gastos registrados para eliminar."
    NO_PAYMENTS_TO_DELETE = "❌ No hay pagos registrados para eliminar."
    NO_PAYMENTS_TO_EDIT = "❌ No hay pagos registrados para editar."
    ITEM_NOT_FOUND = "❌ El elemento seleccionado no se encontró."
    
    # Mensajes generales
    CANCEL_OPERATION = "❌ Operación cancelada."
    LOADING = "⏳ Cargando..."
    FAMILY_INFO = "ℹ️ *Información de la Familia*\n\n*Nombre:* {name}\n*ID de Familia:* `{id}`\n*Miembros:* {members_count}\n\n*Miembros:*\n{members_list}"
    FAMILY_INVITATION = "🔗 *Invitación a la Familia*\n\n*Nombre:* {name}\n*ID:* `{id}`\n\nComparte este ID con las personas que quieras invitar a tu familia."
    
    # Mensajes para balances
    BALANCES_HEADER = "💰 *Balances de la familia*\n\n"
    
    # Mensajes para compartir invitación
    SHARE_INVITATION_INTRO = "🔗 Comparte este enlace para invitar a alguien a unirse a tu familia:"
    
    SHARE_INVITATION_ID = "📝 ID de familia: `{family_id}`\n\nComparte este ID con quien quieras que se una a tu familia."
    
    SHARE_INVITATION_QR = "También pueden escanear este código QR:"
    
    # Mensaje para el enlace de invitación
    INVITATION_LINK = (
        "🔗 *Invitación a la Familia*\n\n"
        "Comparte este código QR o el siguiente enlace para invitar a alguien a unirse a tu familia:\n\n"
        "`{invite_link}`\n\n"
        "Instrucciones para el invitado:\n"
        "1. Haz clic en el enlace o escanea el código QR\n"
        "2. Se abrirá el bot\n"
        "3. Presiona el botón 'INICIAR' o envía /start\n"
        "4. Serás añadido automáticamente a la familia"
    )
    
    # Mensajes específicos del sistema de idiomas
    LANGUAGE_SELECTION = "🌍 Selecciona tu idioma preferido:"
    LANGUAGE_UPDATED = "✅ ¡Idioma actualizado a Español!" 