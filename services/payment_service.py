from services.api_service import ApiService

class PaymentService:
    """Servicio para interactuar con pagos."""
    
    @staticmethod
    def create_payment(from_member, to_member, amount, family_id=None, telegram_id=None):
        """
        Registra un nuevo pago entre dos miembros.
        
        Args:
            from_member (str): ID del miembro que realiza el pago
            to_member (str): ID del miembro que recibe el pago
            amount (float): Monto del pago
            family_id (str, optional): ID de la familia (no se utiliza en el endpoint actual)
            telegram_id (str, optional): ID de Telegram del usuario para autenticación
            
        Returns:
            tuple: (status_code, response_data)
        """
        # Asegurarse de que los valores sean del tipo correcto
        from_member_str = str(from_member) if from_member is not None else None
        to_member_str = str(to_member) if to_member is not None else None
        amount_float = float(amount) if amount is not None else None
        
        # Datos para la solicitud
        data = {
            "from_member": from_member_str,
            "to_member": to_member_str,
            "amount": amount_float
        }
        
        print(f"Datos de solicitud de pago: {data}")
        
        # Usar el endpoint correcto y pasar telegram_id como parámetro de consulta
        return ApiService.request(
            method="POST",
            endpoint="/payments",
            data=data,
            token=telegram_id
        )
    
    @staticmethod
    def get_family_payments(family_id, telegram_id=None):
        """Obtiene los pagos de una familia.
        
        Args:
            family_id: ID de la familia
            telegram_id: ID de Telegram del usuario para autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request(
            "GET", 
            f"/payments/family/{family_id}", 
            token=telegram_id,
            check_status=False
        )
    
    @staticmethod
    def delete_payment(payment_id):
        """Elimina un pago.
        
        Args:
            payment_id: ID del pago (UUID como string)
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request("DELETE", f"/payments/{payment_id}", check_status=False)

    @staticmethod
    def get_payment(payment_id, telegram_id=None):
        """Obtiene un pago específico por su ID.
        
        Args:
            payment_id: ID del pago (UUID como string)
            telegram_id: ID de Telegram del usuario para autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request(
            "GET", 
            f"/payments/{payment_id}", 
            token=telegram_id,
            check_status=False
        )
    
    @staticmethod
    def confirm_payment(payment_id, telegram_id=None):
        """Confirma un pago cambiando su estado a CONFIRM.
        
        Args:
            payment_id: ID del pago (UUID como string)
            telegram_id: ID de Telegram del usuario para autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request(
            "POST",
            f"/payments/{payment_id}/confirm",
            token=telegram_id,
            check_status=False
        )
    
    @staticmethod
    def update_payment_status(payment_id, status, telegram_id=None):
        """Actualiza el estado de un pago.
        
        Args:
            payment_id: ID del pago (UUID como string)
            status: Nuevo estado del pago (PENDING, CONFIRM, INACTIVE)
            telegram_id: ID de Telegram del usuario para autenticación (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        data = {
            "status": status
        }
        
        return ApiService.request(
            "PATCH",
            f"/payments/{payment_id}/status",
            data=data,
            token=telegram_id,
            check_status=False
        ) 