from utils import api_request
from telegram.ext import ContextTypes

def this_user_is_in_family(telegram_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        status_code, response = api_request("GET", f"/members/{telegram_id}", check_status=False)
        
        if status_code == 200 and response and response.get("family_id"):
            family_id = response.get("family_id")
            context.user_data["family_id"] = family_id
            return True
        else:
            return False

    except Exception as e:
        print(f"Error en this_user_is_in_family: {e}")
        return False

def load_family_members(family_id, context: ContextTypes.DEFAULT_TYPE):
    """Carga los miembros de la familia en el contexto.
    
    Args:
        family_id: ID de la familia
        context: Contexto de Telegram
        
    Returns:
        bool: True si se cargaron los miembros correctamente, False en caso contrario
    """
    try:
        # Obtener la información de la familia
        status_code, family = api_request("GET", f"/families/{family_id}", check_status=False)
        
        if status_code == 200 and family and "members" in family:
            # Guardar la familia completa en el contexto
            context.user_data["family_info"] = family
            
            # Crear y guardar un diccionario de ID -> nombre para facilitar la búsqueda
            member_names = {}
            for member in family["members"]:
                member_id = member.get("id", "")
                member_name = member.get("name", f"Usuario {member_id}")
                
                # Guardar por ID
                member_names[member_id] = member_name
                
                # También guardar versiones con prefijos para mayor compatibilidad
                member_names[f"Usuario {member_id}"] = member_name
            
            context.user_data["member_names"] = member_names
            return True
        else:
            print(f"Error al cargar miembros: status_code={status_code}, family={family}")
            return False
            
    except Exception as e:
        print(f"Error en load_family_members: {e}")
        return False

