from utils import api_request

def create_expense(family_id, amount, description, paid_by, split_among=None):
    """Crea un nuevo gasto en la familia.
    
    Args:
        family_id: ID de la familia
        amount: Monto del gasto
        description: Descripción del gasto
        paid_by: ID del miembro que pagó
        split_among: Lista de IDs de miembros entre los que se divide (opcional)
        
    Returns:
        tuple: (status_code, response)
    """
    data = {
        "description": description,
        "amount": amount,
        "paid_by": paid_by
    }
    
    if split_among:
        data["split_among"] = split_among
        
    return api_request("POST", f"/expenses", data, check_status=False)