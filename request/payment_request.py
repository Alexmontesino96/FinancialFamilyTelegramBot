from utils import api_request

def create_payment(family_id, from_member, to_member, amount):
    """Crea un nuevo pago entre miembros de una familia.
    
    Args:
        family_id: ID de la familia
        from_member: ID del miembro que realiza el pago
        to_member: ID del miembro que recibe el pago
        amount: Monto del pago
        
    Returns:
        tuple: (status_code, response)
    """
    data = {
        "from_member": from_member,
        "to_member": to_member,
        "amount": amount
    }
    
    return api_request("POST", "/payments", data, check_status=False)

def get_payments(family_id):
    """Obtiene la lista de pagos de una familia.
    
    Args:
        family_id: ID de la familia
        
    Returns:
        tuple: (status_code, response)
    """
    return api_request("GET", f"/families/{family_id}/payments", check_status=False) 