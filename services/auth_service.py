from services.api_service import ApiService
import traceback

class AuthService:
    """Servicio para manejar la autenticación con la API."""
    
    @staticmethod
    def authenticate(telegram_id):
        """Autentica al usuario con la API y obtiene un token.
        
        En lugar de usar un endpoint específico de autenticación,
        simplemente verificamos si el usuario existe en la API.
        
        Args:
            telegram_id: ID de Telegram del usuario
            
        Returns:
            tuple: (status_code, token)
        """
        try:
            print(f"Verificando si el usuario {telegram_id} existe en la API")
            
            # Verificar si el usuario existe
            status_code, response = ApiService.request("GET", f"/members/{telegram_id}", check_status=False)
            print(f"Respuesta de verificación: status_code={status_code}, response={response}")
            
            if status_code == 200 and response:
                # Si el usuario existe, usamos su ID de Telegram como "token"
                # Esto es un enfoque simplificado que no usa JWT
                print(f"Usuario {telegram_id} existe en la API")
                return status_code, telegram_id
            else:
                error_msg = response.get("detail", "Error desconocido")
                print(f"Error al verificar usuario: {error_msg}")
                return status_code, None
                
        except Exception as e:
            print(f"Error en authenticate: {str(e)}")
            traceback.print_exc()
            return 500, None 