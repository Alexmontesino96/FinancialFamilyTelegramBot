"""
Context Manager Module

This module provides utilities for managing user context data throughout
the bot's conversations. It handles storing and retrieving family information,
member data, and other persistent information needed across different handlers.
"""

from telegram.ext import ContextTypes
from services.family_service import FamilyService
from services.member_service import MemberService
from services.auth_service import AuthService
import traceback

class ContextManager:
    """
    Manager for handling user context data across conversations.
    
    This class provides static methods to check user membership in families,
    load family member information, retrieve context data, and manage the
    user context throughout the bot's operation.
    """
    
    @staticmethod
    async def check_user_in_family(context: ContextTypes.DEFAULT_TYPE, telegram_id: str):
        """
        Verifies if a user is in a family and saves the family ID in the context.
        
        This method checks if the user is already associated with a family and
        stores the family ID in the context for future use if found.
        
        Args:
            context (ContextTypes.DEFAULT_TYPE): Telegram context
            telegram_id (str): Telegram ID of the user
            
        Returns:
            bool: True if the user is in a family, False otherwise
        """
        # Check if we already have the family_id in the context to avoid unnecessary API calls
        if "family_id" in context.user_data:
            print(f"Usuario ya tiene family_id en el contexto: {context.user_data['family_id']}")
            return True
        
        # If not in context, verify with the API if the user is in a family
        print(f"Verificando si el usuario {telegram_id} está en una familia con la API")
        try:
            # Save the Telegram ID in the context for identification purposes
            context.user_data["telegram_id"] = telegram_id
            
            # Get member information directly from the API
            status_code, response = MemberService.get_member(telegram_id)
            
            print(f"Respuesta de get_member: status_code={status_code}, response={response}")
            
            # If the user is in a family, save the family ID in the context
            if status_code == 200 and response and response.get("family_id"):
                family_id = response.get("family_id")
                context.user_data["family_id"] = family_id
                print(f"ID de familia guardado en el contexto: {family_id}")
                
                # También guardamos el ID del miembro para futuras consultas
                if "id" in response:
                    context.user_data["member_id"] = response["id"]
                    print(f"ID del miembro guardado en el contexto: {response['id']}")
                
                # Guardar información del miembro completa si está disponible
                context.user_data["member"] = response
                
                return True
            
            # Si no lo encontramos, intentar una forma alternativa
            if status_code != 200 or not response or not response.get("family_id"):
                print(f"No se encontró familia con el método normal. Código: {status_code}")
                
                # Intentar obtener la información del miembro directamente
                status_code, member = MemberService.get_member(telegram_id)
                
                if status_code == 200 and member and member.get("family_id"):
                    family_id = member.get("family_id")
                    context.user_data["family_id"] = family_id
                    print(f"ID de familia encontrado mediante consulta directa: {family_id}")
                    
                    # Guardar también el ID del miembro y su información
                    if "id" in member:
                        context.user_data["member_id"] = member["id"]
                    context.user_data["member"] = member
                    
                    return True
            
            print("Usuario no está en ninguna familia según la API")
            return False
        except Exception as e:
            # Handle any unexpected errors
            print(f"Error en check_user_in_family: {str(e)}")
            traceback.print_exc()
            
            # Último intento: consultar directamente por el telegram_id
            try:
                print("Intentando obtener miembro directamente como último recurso")
                status_code, member = MemberService.get_member(telegram_id)
                
                if status_code == 200 and member and member.get("family_id"):
                    family_id = member.get("family_id")
                    context.user_data["family_id"] = family_id
                    print(f"ID de familia obtenido en último intento: {family_id}")
                    
                    # Guardar también datos del miembro
                    if "id" in member:
                        context.user_data["member_id"] = member["id"]
                    context.user_data["member"] = member
                    
                    return True
            except Exception as inner_e:
                print(f"Error en último intento de obtener miembro: {str(inner_e)}")
                traceback.print_exc()
            
            return False
    
    @staticmethod
    async def load_family_members(context: ContextTypes.DEFAULT_TYPE, family_id: str):
        """
        Loads family member information into the context.
        
        This method retrieves all members of a family and stores their names
        and IDs in the context for easy access throughout conversations.
        
        Args:
            context (ContextTypes.DEFAULT_TYPE): Telegram context
            family_id (str): ID of the family to load members from
            
        Returns:
            bool: True if members were loaded successfully, False otherwise
        """
        try:
            # Get the Telegram ID from the context for authentication
            telegram_id = context.user_data.get("telegram_id")
            
            if not telegram_id:
                print("No se encontró telegram_id en el contexto")
                return False
            
            # Get family information from the API
            print(f"Cargando miembros de la familia {family_id} con telegram_id={telegram_id}")
            status_code, family = FamilyService.get_family(family_id, telegram_id)
            
            print(f"Respuesta de get_family: status_code={status_code}, family={family}")
            
            # If there was an error or no family was found, return False
            if status_code != 200 or not family:
                print(f"Error al obtener la familia: status_code={status_code}")
                return False
            
            # Extract member information and store in the context
            members = family.get("members", [])
            
            # Create a dictionary mapping member IDs to names for easy lookup
            member_names = {}
            for member in members:
                member_id = member.get("id")
                member_name = member.get("name", "Unknown")
                if member_id:
                    # Asegurarnos de que los IDs se guarden como strings
                    member_names[str(member_id)] = member_name
                    # También guardar el mismo valor con el ID como integer, para compatibilidad
                    if isinstance(member_id, int) or (isinstance(member_id, str) and member_id.isdigit()):
                        numeric_id = int(member_id) if isinstance(member_id, str) else member_id
                        member_names[numeric_id] = member_name
            
            # Save the member names dictionary in the context
            context.user_data["member_names"] = member_names
            print(f"Nombres de miembros guardados en el contexto: {member_names}")
            
            # Also save the complete family information for reference
            context.user_data["family"] = family
            
            return True
        except Exception as e:
            # Handle any unexpected errors
            print(f"Error en load_family_members: {str(e)}")
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_family_id(context: ContextTypes.DEFAULT_TYPE):
        """
        Retrieves the family ID from the context.
        
        Args:
            context (ContextTypes.DEFAULT_TYPE): Telegram context
            
        Returns:
            str: The family ID or None if not found
        """
        # Get the family ID from the context if available
        family_id = context.user_data.get("family_id")
        
        if not family_id:
            print("No se encontró family_id en el contexto")
        
        return family_id
    
    @staticmethod
    def get_member_names(context: ContextTypes.DEFAULT_TYPE):
        """
        Retrieves the dictionary of member names from the context.
        
        Args:
            context (ContextTypes.DEFAULT_TYPE): Telegram context
            
        Returns:
            dict: Dictionary mapping member IDs to names, or empty dict if not found
        """
        # Get the member names dictionary from the context if available
        member_names = context.user_data.get("member_names", {})
        
        if not member_names:
            print("No se encontraron nombres de miembros en el contexto")
        
        return member_names
    
    @staticmethod
    def get_telegram_id(context: ContextTypes.DEFAULT_TYPE):
        """
        Retrieves the Telegram ID from the context.
        
        Args:
            context (ContextTypes.DEFAULT_TYPE): Telegram context
            
        Returns:
            str: The Telegram ID or None if not found
        """
        # Get the Telegram ID from the context if available
        telegram_id = context.user_data.get("telegram_id")
        
        if not telegram_id:
            print("No se encontró telegram_id en el contexto")
        
        return telegram_id
    
    @staticmethod
    def clear_context(context: ContextTypes.DEFAULT_TYPE, keys=None):
        """
        Clears specific keys or the entire user context.
        
        Args:
            context (ContextTypes.DEFAULT_TYPE): Telegram context
            keys (list, optional): List of keys to clear. If None, clears all keys.
            
        Returns:
            bool: True if the context was cleared successfully
        """
        try:
            # If specific keys are provided, clear only those keys
            if keys:
                for key in keys:
                    if key in context.user_data:
                        del context.user_data[key]
                        print(f"Clave {key} eliminada del contexto")
            # Otherwise, clear the entire user_data dictionary
            else:
                context.user_data.clear()
                print("Contexto completamente limpiado")
            
            return True
        except Exception as e:
            # Handle any unexpected errors
            print(f"Error en clear_context: {str(e)}")
            traceback.print_exc()
            return False 