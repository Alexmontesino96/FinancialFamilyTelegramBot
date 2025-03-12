from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

class Keyboards:
    """Teclados personalizados para Telegram."""
    
    @staticmethod
    def get_main_menu_keyboard():
        """Devuelve el teclado del menú principal."""
        keyboard = [
            ["💰 Ver Balances", "💸 Crear Gasto"],
            ["📜 Listar Registros", "💳 Registrar Pago"],
            ["✏️ Editar/Eliminar", "ℹ️ Info Familia"],
            ["🔗 Compartir Invitación"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_edit_options_keyboard():
        """Devuelve el teclado con opciones para editar/eliminar gastos o pagos."""
        keyboard = [
            ["📝 Editar Gastos", "🗑️ Eliminar Gastos"],
            ["📝 Editar Pagos", "🗑️ Eliminar Pagos"],
            ["↩️ Volver al Menú"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_start_keyboard():
        """Devuelve el teclado inicial con opciones para crear o unirse a una familia."""
        keyboard = [
            ["🏠 Crear Familia Nueva"],
            ["🔗 Unirse a Familia Existente"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_confirmation_keyboard():
        """Devuelve el teclado de confirmación."""
        keyboard = [
            ["✅ Confirmar", "❌ Cancelar"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_cancel_keyboard():
        """Devuelve el teclado con solo la opción de cancelar."""
        keyboard = [["❌ Cancelar"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def get_list_options_keyboard():
        """Devuelve el teclado con opciones para listar gastos o pagos."""
        keyboard = [
            ["📋 Listar Gastos", "📊 Listar Pagos"],
            ["↩️ Volver al Menú"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    @staticmethod
    def remove_keyboard():
        """Devuelve un objeto para eliminar el teclado."""
        return ReplyKeyboardRemove() 