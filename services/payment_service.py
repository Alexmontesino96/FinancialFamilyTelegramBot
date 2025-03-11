from services.api_service import ApiService

class PaymentService:
    """Servicio para interactuar con pagos."""
    
    @staticmethod
    def create_payment(from_member, to_member, amount, family_id, telegram_id=None):
        """Crea un nuevo pago.
        
        Args:
            from_member: ID del miembro que realiza el pago
            to_member: ID del miembro que recibe el pago
            amount: Monto del pago
            family_id: ID de la familia
            telegram_id: ID de Telegram del usuario (opcional)
            
        Returns:
            tuple: (status_code, response)
        """
        data = {
            "from_member": from_member,
            "to_member": to_member,
            "amount": amount,
            "family_id": family_id
        }
        
        # Usar el endpoint correcto para pagos
        return ApiService.request("POST", "/payments", data, token=telegram_id, check_status=False)
    
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