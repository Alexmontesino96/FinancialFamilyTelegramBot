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
        # La ruta para obtener miembros por ID de Telegram es /members/{telegram_id}
        status_code, response = ApiService.request("GET", f"/members/{telegram_id}", token=token, check_status=False)
        print(f"Respuesta de get_member: status_code={status_code}, response={response}")
        return status_code, response
    
    @staticmethod
    def get_member_by_id(member_id, token=None):
        """Obtiene información de un miembro por su ID.
        
        Args:
            member_id: ID del miembro o diccionario con datos del miembro
            token: Token de autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        # Verificar si member_id es un diccionario (objeto completo)
        if isinstance(member_id, dict):
            # Extraer el ID del diccionario
            if "id" in member_id:
                actual_id = member_id["id"]
                print(f"Se pasó un objeto miembro completo, extrayendo ID: {actual_id}")
                member_id = actual_id
            else:
                print(f"Se pasó un diccionario sin campo 'id', usando como está: {member_id}")
        
        print(f"Obteniendo información del miembro con ID: {member_id}")
        
        # Verificar si el ID parece ser un UUID (contiene guiones o letras)
        is_uuid = isinstance(member_id, str) and ('-' in member_id or any(c.isalpha() for c in member_id))
        
        # Todos los IDs (numéricos o UUIDs) usan la misma ruta en este endpoint
        status_code, response = ApiService.request("GET", f"/members/id/{member_id}", token=token, check_status=False)
        print(f"Respuesta de get_member_by_id: status_code={status_code}, response={response}")
        return status_code, response
    
    @staticmethod
    def get_member_by_uuid(uuid, token=None):
        """Obtiene información de un miembro por su UUID.
        
        Args:
            uuid: UUID del miembro o diccionario con datos del miembro
            token: Token de autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        # Verificar si uuid es un diccionario (objeto completo)
        if isinstance(uuid, dict):
            # Extraer el ID del diccionario
            if "id" in uuid:
                actual_uuid = uuid["id"]
                print(f"Se pasó un objeto miembro completo a get_member_by_uuid, extrayendo UUID: {actual_uuid}")
                uuid = actual_uuid
            else:
                print(f"Se pasó un diccionario sin campo 'id' a get_member_by_uuid, usando como está: {uuid}")
                
        print(f"Obteniendo información del miembro con UUID: {uuid}")
        # Usar la ruta correcta para UUIDs: /members/id/{uuid}
        status_code, response = ApiService.request("GET", f"/members/id/{uuid}", token=token, check_status=False)
        print(f"Respuesta de get_member_by_uuid: status_code={status_code}, response={response}")
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