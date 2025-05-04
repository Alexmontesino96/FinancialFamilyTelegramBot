import requests
from telegram import Update
from telegram.ext import ContextTypes

# URL base de la API (ajusta según tu configuración)
API_BASE_URL = "http://127.0.0.1:8007"

def api_request(method, endpoint, data=None, params=None):
    """Realiza una solicitud HTTP a la API."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, params=params)
        elif method == "DELETE":
            response = requests.delete(url, params=params)
        response.raise_for_status()
        return response.json() if response.content else {"message": "Success"}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la API: {str(e)}")

def format_members(members):
    """Formatea la lista de miembros para mostrar en Telegram."""
    return "\n".join([f"- ID: {m['id']}, Nombre: {m['name']}, Teléfono: {m['phone']}" for m in members])

def format_expenses(expenses):
    return "\n".join([
        f"- ID: {e['id']}, Descripción: {e['description']}, Monto: {e['amount']}, "
        f"Pagado por: {e['paid_by']}, Dividido entre: {e['split_among']}, Fecha: {e['date']}"
        for e in expenses
    ])

def format_balances(balances):
    result = []
    for b in balances:
        debts = ", ".join([f"{d['to']} ({d['amount']})" for d in b['debts']]) if b['debts'] else "Ninguna"
        credits = ", ".join([f"{c['from']} ({c['amount']})" for c in b['credits']]) if b['credits'] else "Ninguna"
        result.append(
            f"Miembro: {b['name']} (ID: {b['member_id']})\n"
            f"Deuda total: {b['total_debt']}, Crédito total: {b['total_owed']}, Balance neto: {b['net_balance']}\n"
            f"Deudas: {debts}\nCréditos: {credits}"
        )
    return "\n\n".join(result)

async def send_error(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    """Envía un mensaje de error al usuario."""
    await update.message.reply_text(f"❌ Error: {message}")

def get_user_family_id(telegram_id):
    """Obtiene el ID de la familia a la que pertenece un usuario.
    
    Args:
        telegram_id: ID de Telegram del usuario
        
    Returns:
        str: ID de la familia, o None si no pertenece a ninguna
    """
    try:
        response = api_request("GET", f"/members/by-telegram-id/{telegram_id}")
        if response and "family_id" in response:
            return response["family_id"]
        return None
    except Exception:
        return None