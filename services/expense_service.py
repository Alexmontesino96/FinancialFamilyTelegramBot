"""
Expense Service Module

This module provides services for managing expenses in the application.
It handles expense creation, retrieval, updating, and deletion.
"""

from services.api_service import ApiService
import traceback

class ExpenseService:
    """
    Service for interacting with expense-related API endpoints.
    
    This class provides methods to create, retrieve, update, and delete expenses,
    as well as to get all expenses for a specific family.
    """
    
    @staticmethod
    def create_expense(description, amount, paid_by, family_id, telegram_id=None):
        """
        Creates a new expense.
        
        Args:
            description (str): Description of the expense
            amount (float): Amount of the expense
            paid_by (str): ID of the member who paid
            family_id (str): ID of the family
            telegram_id (str, optional): Telegram ID of the user creating the expense
            
        Returns:
            tuple: (status_code, response)
        """
        try:
            print(f"Creando gasto: description={description}, amount={amount}, paid_by={paid_by}, family_id={family_id}, telegram_id={telegram_id}")
            data = {
                "description": description,
                "amount": amount,
                "paid_by": paid_by
            }
            # Usar el endpoint correcto de la API
            endpoint = "/expenses"
            status_code, response = ApiService.request("POST", endpoint, data, token=telegram_id, params={"telegram_id": telegram_id}, check_status=False)
            print(f"Resultado de create_expense: status_code={status_code}, response={response}")
            
            # Verificar si la respuesta es válida
            if status_code in [200, 201] and response:
                print(f"Gasto creado exitosamente: {response}")
                return status_code, response
            else:
                print(f"Error al crear gasto: status_code={status_code}, response={response}")
                return status_code, response
        except Exception as e:
            print(f"Excepción en create_expense: {str(e)}")
            traceback.print_exc()
            return 500, {"error": f"Error al crear gasto: {str(e)}"}
    
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