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
    def get_family_payments(family_id):
        """Obtiene los pagos de una familia.
        
        Args:
            family_id: ID de la familia
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request("GET", f"/families/{family_id}/payments", check_status=False)
    
    @staticmethod
    def delete_payment(payment_id):
        """Elimina un pago.
        
        Args:
            payment_id: ID del pago (UUID como string)
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request("DELETE", f"/payments/{payment_id}", check_status=False) 