"""
API Service Module

This module provides a service for interacting with the backend API.
It handles HTTP requests, error handling, and response processing.
"""

import requests
import traceback
from config import API_BASE_URL, logger

class ApiService:
    """
    Base service for interacting with the API.
    
    This class provides methods to make HTTP requests to the backend API,
    handle responses, and manage errors in a consistent way.
    """
    
    @staticmethod
    def request(method, endpoint, data=None, token=None, check_status=True):
        """
        Makes an HTTP request to the API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            data (dict, optional): Data to send in the request
            token (str, optional): Authentication token or Telegram ID
            check_status (bool, optional): If True, raises an exception if status code indicates error
            
        Returns:
            tuple: (status_code, response_data)
        """
        # Asegurarse de que el endpoint comience con una barra diagonal
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            
        url = f"{API_BASE_URL}{endpoint}"
        logger.debug(f"Making {method} request to {url}")
        if data:
            logger.debug(f"Request data: {data}")
            
        try:
            # Configurar headers para JSON
            headers = {'Content-Type': 'application/json'}
            
            # Añadir identificación si está disponible
            # En lugar de usar un token JWT, simplemente pasamos el ID de Telegram
            # como un parámetro de consulta o en los datos
            params = {}
            if token and isinstance(token, str):
                # Usar el token como ID de Telegram en un parámetro de consulta
                params['telegram_id'] = token
                logger.debug(f"Including telegram_id={token} in request")
            
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=15)
            elif method == "POST":
                # Para solicitudes POST, solo incluir el telegram_id en los parámetros de consulta
                # y no duplicarlo en el cuerpo de la solicitud
                response = requests.post(url, json=data, params=params, headers=headers, timeout=15)
            elif method == "PUT":
                # Para solicitudes PUT, solo incluir el telegram_id en los parámetros de consulta
                # y no duplicarlo en el cuerpo de la solicitud
                response = requests.put(url, json=data, params=params, headers=headers, timeout=15)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers, timeout=15)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return 400, {"error": f"Unsupported HTTP method: {method}"}
            
            # Obtener el status code
            status_code = response.status_code
            logger.debug(f"Response status code: {status_code}")
            
            # Intentar obtener el contenido como JSON
            try:
                if response.content:
                    response_data = response.json()
                else:
                    response_data = {}
            except ValueError:
                logger.warning(f"Response is not valid JSON: {response.content}")
                response_data = {"error": "Response is not valid JSON", "content": str(response.content)}
            
            # Verificar si hubo un error
            if check_status and status_code >= 400:
                error_message = response_data.get("detail", "Unknown error")
                logger.error(f"Request error: {error_message}")
                
            return status_code, response_data
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            traceback.print_exc()
            return 503, {"error": f"Connection error: {str(e)}"}
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            traceback.print_exc()
            return 504, {"error": f"Request timeout: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            traceback.print_exc()
            return 500, {"error": f"Unexpected error: {str(e)}"}
            
    @staticmethod
    def api_request(method, endpoint, data=None, token=None, check_status=True):
        """
        Alias for request method to maintain compatibility.
        
        This method simply calls the request method with the same parameters.
        It exists for backward compatibility with older code.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            data (dict, optional): Data to send in the request
            token (str, optional): Authentication token or Telegram ID
            check_status (bool, optional): If True, raises an exception if status code indicates error
            
        Returns:
            tuple: (status_code, response_data)
        """
        return ApiService.request(method, endpoint, data, token, check_status)