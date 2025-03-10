"""
Configuration Module

This module loads environment variables from .env file and defines
conversation states used throughout the application.
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO if os.getenv('DEBUG', 'False').lower() != 'true' else logging.DEBUG
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables!")
    raise ValueError("BOT_TOKEN environment variable is required")

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8099')

# Conversation states for different flows
# Start flow - Family creation and joining
ASK_FAMILY_CODE = 0  # State for asking if user wants to create or join a family
ASK_FAMILY_NAME = 1  # State for asking the family name when creating
ASK_USER_NAME = 2    # State for asking the user's name
JOIN_FAMILY_CODE = 3 # State for asking the family code when joining

# Expense flow - Creating and managing expenses
DESCRIPTION = 4      # State for asking expense description
AMOUNT = 5           # State for asking expense amount
CONFIRM = 6          # State for confirming expense creation

# Payment flow - Registering payments between members
SELECT_TO_MEMBER = 7  # State for selecting the member to pay
PAYMENT_AMOUNT = 8    # State for entering payment amount
PAYMENT_CONFIRM = 9   # State for confirming payment

# Edit/Delete flow - Modifying or removing records
EDIT_OPTION = 10      # State for selecting edit option (expense or payment)
SELECT_EXPENSE = 11   # State for selecting which expense to edit/delete
SELECT_PAYMENT = 12   # State for selecting which payment to edit/delete
CONFIRM_DELETE = 13   # State for confirming deletion
EDIT_EXPENSE_AMOUNT = 14  # State for editing expense amount 