from utils import api_request


def get_balance_by_user(family_id, user_id):
    """Obtiene el balance de un usuario en una familia.
    
    Args:
        family_id: ID de la familia
        user_id: ID del usuario
        
    Returns:
        dict: Balance del usuario o None si hay un error
    """
    status_code, response = api_request("GET", f"/balances/{family_id}/{user_id}", check_status=False)
    if status_code == 200 and response:
        return response
    else:
        print(f"Error al obtener balance. Status code: {status_code}, Response: {response}")
        return None