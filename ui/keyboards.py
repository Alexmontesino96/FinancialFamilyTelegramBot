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
            ["🏠 Crear Familia"],
            ["🔗 Unirse a Familia"]
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