from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from languages.utils.translator import get_message, DEFAULT_LANGUAGE

class Keyboards:
    """Teclados personalizados para Telegram."""
    
    # Textos por defecto (para cuando no se proporciona user_id)
    DEFAULT_TEXTS = {
        "VIEW_BALANCES": "💰 Ver Balances",
        "CREATE_EXPENSE": "💸 Crear Gasto",
        "LIST_RECORDS": "📜 Listar Registros",
        "REGISTER_PAYMENT": "💳 Registrar Pago",
        "EDIT_DELETE": "✏️ Editar/Eliminar",
        "FAMILY_INFO": "ℹ️ Info Familia",
        "SHARE_INVITATION": "🔗 Compartir Invitación",
        "CHANGE_LANGUAGE": "🌍 Cambiar Idioma",
        "EDIT_EXPENSES": "📝 Editar Gastos",
        "DELETE_EXPENSES": "🗑️ Eliminar Gastos",
        "EDIT_PAYMENTS": "📝 Editar Pagos",
        "DELETE_PAYMENTS": "🗑️ Eliminar Pagos",
        "BACK_TO_MENU": "↩️ Volver al Menú",
        "CREATE_FAMILY": "🏠 Crear Familia",
        "JOIN_FAMILY": "🔗 Unirse a Familia",
        "CONFIRM": "✅ Confirmar",
        "CANCEL": "❌ Cancelar",
        "LIST_EXPENSES": "📋 Listar Gastos",
        "LIST_PAYMENTS": "📊 Listar Pagos"
    }

    @staticmethod
    def get_text(user_id, key):
        """
        Obtiene un texto traducido para botones de teclado.
        Si no se proporciona user_id o hay un error, usa el texto por defecto.
        """
        if not user_id:
            return Keyboards.DEFAULT_TEXTS.get(key, key)
        
        try:
            return get_message(user_id, f"KB_{key}")
        except:
            return Keyboards.DEFAULT_TEXTS.get(key, key)
    
    @staticmethod
    def get_main_menu_keyboard(user_id=None):
        """Devuelve el teclado del menú principal."""
        keyboard = [
            [
                Keyboards.get_text(user_id, "VIEW_BALANCES"), 
                Keyboards.get_text(user_id, "CREATE_EXPENSE")
            ],
            [
                Keyboards.get_text(user_id, "LIST_RECORDS"), 
                Keyboards.get_text(user_id, "REGISTER_PAYMENT")
            ],
            [
                Keyboards.get_text(user_id, "EDIT_DELETE"), 
                Keyboards.get_text(user_id, "FAMILY_INFO")
            ],
            [
                Keyboards.get_text(user_id, "SHARE_INVITATION"), 
                Keyboards.get_text(user_id, "CHANGE_LANGUAGE")
            ]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_edit_options_keyboard(user_id=None):
        """Devuelve el teclado con opciones para editar/eliminar gastos o pagos."""
        keyboard = [
            [
                Keyboards.get_text(user_id, "EDIT_EXPENSES"), 
                Keyboards.get_text(user_id, "DELETE_EXPENSES")
            ],
            [
                Keyboards.get_text(user_id, "EDIT_PAYMENTS"), 
                Keyboards.get_text(user_id, "DELETE_PAYMENTS")
            ],
            [Keyboards.get_text(user_id, "BACK_TO_MENU")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_start_keyboard(user_id=None):
        """Devuelve el teclado inicial con opciones para crear o unirse a una familia."""
        keyboard = [
            [Keyboards.get_text(user_id, "CREATE_FAMILY")],
            [Keyboards.get_text(user_id, "JOIN_FAMILY")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_confirmation_keyboard(user_id=None):
        """Devuelve el teclado de confirmación."""
        keyboard = [
            [
                Keyboards.get_text(user_id, "CONFIRM"), 
                Keyboards.get_text(user_id, "CANCEL")
            ]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_cancel_keyboard(user_id=None):
        """Devuelve el teclado con solo la opción de cancelar."""
        keyboard = [[Keyboards.get_text(user_id, "CANCEL")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_list_options_keyboard(user_id=None):
        """Devuelve el teclado con opciones para listar gastos o pagos."""
        keyboard = [
            [
                Keyboards.get_text(user_id, "LIST_EXPENSES"), 
                Keyboards.get_text(user_id, "LIST_PAYMENTS")
            ],
            [Keyboards.get_text(user_id, "BACK_TO_MENU")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def remove_keyboard():
        """Elimina cualquier teclado personalizado."""
        return ReplyKeyboardRemove()
        
    @staticmethod
    def get_expense_division_keyboard():
        """Devuelve un teclado para seleccionar cómo dividir el gasto."""
        keyboard = [
            ["👥 Dividir entre todos (por defecto)"],
            ["👤 Seleccionar miembros específicos"],
            ["❌ Cancelar"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
    @staticmethod
    def get_select_members_keyboard(members, preselected_ids=None):
        """
        Genera un teclado con opciones para seleccionar miembros.
        
        Args:
            members (list): Lista de miembros de la familia
            preselected_ids (list): Lista de IDs de miembros preseleccionados
            
        Returns:
            ReplyKeyboardMarkup: Teclado con opciones de selección
        """
        if preselected_ids is None:
            preselected_ids = []
            
        keyboard = []
        for member in members:
            member_id = str(member.get("id"))
            member_name = member.get("name", f"Usuario {member_id}")
            checked = "✅" if member_id in preselected_ids else "⬜"
            keyboard.append([f"{checked} {member_name}"])
        
        keyboard.append(["✅ Seleccionar todos"])
        keyboard.append(["⬜ Deseleccionar todos"])
        keyboard.append(["✓ Continuar"])
        keyboard.append(["❌ Cancelar"])
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False) 