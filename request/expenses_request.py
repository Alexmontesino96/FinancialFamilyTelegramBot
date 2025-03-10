from utils import api_request

def create_expense(amount, description, payer_id):
    """Crea un gasto en la familia."""
    return api_request("POST", f"/expenses", data={"amount": amount, "description": description, "paid_by": payer_id})

