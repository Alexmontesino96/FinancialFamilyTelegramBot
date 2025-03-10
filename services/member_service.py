from services.api_service import ApiService

class MemberService:
    """Servicio para interactuar con miembros."""
    
    @staticmethod
    def get_member(telegram_id, token=None):
        """Obtiene información de un miembro por su ID de Telegram.
        
        Args:
            telegram_id: ID de Telegram del miembro
            token: Token de autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        print(f"Obteniendo información del miembro con telegram_id: {telegram_id}")
        status_code, response = ApiService.request("GET", f"/members/{telegram_id}", token=token, check_status=False)
        print(f"Respuesta de get_member: status_code={status_code}, response={response}")
        return status_code, response
    
    @staticmethod
    def get_member_by_id(member_id, token=None):
        """Obtiene información de un miembro por su ID.
        
        Args:
            member_id: ID del miembro
            token: Token de autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        print(f"Obteniendo información del miembro con ID: {member_id}")
        status_code, response = ApiService.request("GET", f"/members/id/{member_id}", token=token, check_status=False)
        print(f"Respuesta de get_member_by_id: status_code={status_code}, response={response}")
        return status_code, response
    
    @staticmethod
    def update_member(member_id, data, token=None):
        """Actualiza la información de un miembro.
        
        Args:
            member_id: ID del miembro
            data: Datos a actualizar
            token: Token de autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        print(f"Actualizando información del miembro con ID: {member_id}")
        status_code, response = ApiService.request("PUT", f"/members/{member_id}", data, token=token, check_status=False)
        print(f"Respuesta de update_member: status_code={status_code}, response={response}")
        return status_code, response 