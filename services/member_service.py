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
        
        # Verificar si el ID parece ser un UUID (contiene guiones o letras)
        is_uuid = isinstance(member_id, str) and ('-' in member_id or any(c.isalpha() for c in member_id))
        
        if is_uuid:
            # Si es un UUID, usar el nuevo endpoint para UUIDs
            print(f"Detectado ID formato UUID, usando endpoint UUID")
            return MemberService.get_member_by_uuid(member_id, token)
        
        # Si no es UUID, continuar con el endpoint original para IDs numéricos
        status_code, response = ApiService.request("GET", f"/members/id/{member_id}", token=token, check_status=False)
        print(f"Respuesta de get_member_by_id: status_code={status_code}, response={response}")
        return status_code, response
    
    @staticmethod
    def get_member_by_uuid(uuid, token=None):
        """Obtiene información de un miembro por su UUID.
        
        Args:
            uuid: UUID del miembro
            token: Token de autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        print(f"Obteniendo información del miembro con UUID: {uuid}")
        status_code, response = ApiService.request("GET", f"/members/uuid/{uuid}", token=token, check_status=False)
        
        # Si la API no tiene un endpoint específico para UUID, intentar obtenerlo por otra vía
        if status_code == 404 or status_code >= 400:
            print(f"Endpoint de UUID no encontrado o error, intentando buscar miembro en la familia")
            # Intentar obtener la familia y buscar al miembro por su ID en la lista de miembros
            from services.family_service import FamilyService
            
            # Primero obtener el ID de familia del contexto o desde otra fuente
            # Nota: Esto asume que ya tienes el family_id disponible en algún lugar
            # Si no lo tienes, necesitarás implementar otra estrategia
            try:
                # Intentar buscar en todas las familias disponibles si es posible
                # Esto es una solución alternativa y podría no ser eficiente
                family_id = response.get("family_id") if isinstance(response, dict) else None
                
                if not family_id:
                    print("No se pudo obtener el ID de familia, buscando por UUID fallará")
                    return status_code, response
                
                status_code, family = FamilyService.get_family(family_id, token)
                
                if status_code == 200 and family and "members" in family:
                    # Buscar el miembro por UUID en la lista de miembros de la familia
                    for member in family.get("members", []):
                        if member.get("id") == uuid:
                            print(f"Miembro encontrado en la familia: {member}")
                            return 200, member
                    
                    print(f"Miembro con UUID {uuid} no encontrado en la familia")
                else:
                    print(f"No se pudo obtener información de la familia: {status_code}")
            except Exception as e:
                print(f"Error al intentar buscar miembro en la familia: {str(e)}")
        
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