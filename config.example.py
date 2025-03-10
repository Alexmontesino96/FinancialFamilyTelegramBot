# Configuración del bot
BOT_TOKEN = 'TU_TOKEN_DE_TELEGRAM_AQUI'  # Reemplaza con tu token de bot de Telegram

# Configuración de la API
API_BASE_URL = "http://localhost:8099"  # URL base de la API

# Estados para los flujos de conversación
# Flujo de inicio
ASK_FAMILY_CODE = 0
ASK_FAMILY_NAME = 1
ASK_USER_NAME = 2
JOIN_FAMILY_CODE = 3

# Flujo de gastos
DESCRIPTION = 4
AMOUNT = 5
CONFIRM = 6

# Flujo de pagos
SELECT_TO_MEMBER = 7
PAYMENT_AMOUNT = 8
PAYMENT_CONFIRM = 9

# Flujo de edición/eliminación
EDIT_OPTION = 10
SELECT_EXPENSE = 11
SELECT_PAYMENT = 12
CONFIRM_DELETE = 13
EDIT_EXPENSE_AMOUNT = 14 