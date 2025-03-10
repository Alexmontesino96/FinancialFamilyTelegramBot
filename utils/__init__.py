import requests
from config import API_BASE_URL

def api_request(method, endpoint, data=None, check_status=True):
    """Realiza una solicitud HTTP a la API.
    
    Args:
        method: Método HTTP (GET, POST, PUT, DELETE)
        endpoint: Endpoint de la API
        data: Datos a enviar en la solicitud (opcional)
        check_status: Si es True, lanza una excepción si el status code es un error
        
    Returns:
        tuple: (status_code, response_data)
    """
    url = f"{API_BASE_URL}{endpoint}"
    print(f"Realizando solicitud {method} a {url}")
    if data:
        print(f"Datos: {data}")
        
    try:
        # Configurar headers para JSON
        headers = {'Content-Type': 'application/json'}
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        # Obtener el status code
        status_code = response.status_code
        print(f"Status code: {status_code}")
        
        # Intentar obtener el contenido como JSON
        try:
            if response.content:
                response_data = response.json()
            else:
                response_data = {"message": "Success"}
        except Exception as e:
            print(f"Error al parsear la respuesta como JSON: {e}")
            print(f"Contenido de la respuesta: {response.content}")
            response_data = {"message": "Error parsing response", "content": str(response.content)}
        
        print(f"Respuesta: status_code={status_code}, data={response_data}")
        
        # Si check_status es True, lanzar excepción si hay error
        if check_status:
            response.raise_for_status()
            
        # Devolver status_code y datos
        return status_code, response_data
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        # Si hay una excepción, devolver el status code (si está disponible) y None como datos
        if 'response' in locals() and hasattr(response, 'status_code'):
            return response.status_code, None
        # Si no hay status_code disponible, devolver 500 como código genérico de error
        return 500, None
