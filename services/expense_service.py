"""
Expense Service Module

This module provides services for managing expenses in the application.
It handles expense creation, retrieval, updating, and deletion.
"""

from services.api_service import ApiService
import traceback
import requests

class ExpenseService:
    """
    Service for interacting with expense-related API endpoints.
    
    This class provides methods to create, retrieve, update, and delete expenses,
    as well as to get all expenses for a specific family.
    """
    
    @staticmethod
    def create_expense(description, amount, paid_by, family_id, telegram_id=None, split_among=None):
        """
        Crea un nuevo gasto.
        
        Args:
            description (str): Descripción del gasto
            amount (float): Monto del gasto
            paid_by (str): ID del miembro que pagó el gasto
            family_id (str): ID de la familia del gasto
            telegram_id (str, opcional): ID de Telegram para validación
            split_among (list, opcional): Lista de IDs de miembros entre los que dividir el gasto
            
        Returns:
            tuple: (status_code, response_json)
        """
        try:
            # Construir la URL para la solicitud
            url = f"{API_BASE_URL}/expenses/"
            
            # Preparar los datos para la solicitud
            expense_data = {
                "description": description,
                "amount": amount,
                "paid_by": paid_by
            }
            
            # Añadir split_among solo si está especificado
            if split_among is not None:
                expense_data["split_among"] = split_among
            
            # Parámetros para la solicitud
            params = {}
            if telegram_id:
                params["telegram_id"] = telegram_id
                
            print(f"[API] Creando gasto con datos: {expense_data} y params: {params}")
            
            # Realizar la solicitud POST a la API
            response = requests.post(
                url,
                json=expense_data,
                params=params
            )
            
            # Parsear y devolver la respuesta
            status_code = response.status_code
            
            try:
                response_json = response.json()
            except ValueError:
                # Si no es JSON válido, usar el texto como respuesta
                response_json = {"detail": response.text}
                
            return status_code, response_json
            
        except Exception as e:
            print(f"Error en create_expense: {str(e)}")
            return 500, {"detail": str(e)}
    
    @staticmethod
    def get_family_expenses(family_id, telegram_id=None):
        """
        Retrieves all expenses for a specific family.
        
        Args:
            family_id (str): ID of the family (UUID as string)
            telegram_id (str, optional): Telegram ID of the user
            
        Returns:
            tuple: (status_code, response)
        """
        print(f"Obteniendo gastos para la familia con ID: {family_id}, telegram_id: {telegram_id}")
        
        # Verificar que family_id sea un valor válido
        if not family_id:
            print("Error: family_id es None o vacío")
            return 400, {"error": "ID de familia no válido"}
        
        # Ya no necesitamos convertir family_id a entero, ahora es un UUID como string
        
        # Llamar a la API con el ID de Telegram si está disponible
        return ApiService.request("GET", f"/expenses/family/{family_id}", token=telegram_id, check_status=False)
    
    @staticmethod
    def get_expense(expense_id):
        """
        Retrieves information about a specific expense.
        
        Args:
            expense_id (str): ID of the expense (UUID as string)
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request("GET", f"/expenses/{expense_id}", check_status=False)
    
    @staticmethod
    def update_expense(expense_id, data, telegram_id=None):
        """
        Updates an existing expense.
        
        Args:
            expense_id (str): ID of the expense (UUID as string)
            data (dict): Data to update (dictionary)
            telegram_id (str, optional): Telegram ID of the user
            
        Returns:
            tuple: (status_code, response)
        """
        try:
            print(f"Actualizando gasto con ID: {expense_id}, datos: {data}, telegram_id: {telegram_id}")
            
            # Usar el endpoint PUT para actualizar el gasto
            status_code, response = ApiService.request("PUT", f"/expenses/{expense_id}", data, token=telegram_id, check_status=False)
            print(f"Resultado de update_expense: status_code={status_code}, response={response}")
            
            if status_code >= 400:
                print(f"Error al actualizar gasto: status_code={status_code}, response={response}")
            
            return status_code, response
        except Exception as e:
            print(f"Excepción en update_expense: {str(e)}")
            traceback.print_exc()
            return 500, {"error": f"Error al actualizar gasto: {str(e)}"}
    
    @staticmethod
    def delete_expense(expense_id):
        """
        Deletes an expense.
        
        Args:
            expense_id (str): ID of the expense (UUID as string)
            
        Returns:
            tuple: (status_code, response)
        """
        return ApiService.request("DELETE", f"/expenses/{expense_id}", check_status=False)