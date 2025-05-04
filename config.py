"""
Configuration Module for the Financial Bot

This module contains configuration constants and environment variables used throughout the application.
"""

import os
import logging
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Check if we're running inside Docker or on Render 
IS_DOCKER = os.environ.get('DOCKER', 'false').lower() == 'true'
IS_RENDER = os.environ.get('RENDER', 'false').lower() == 'true'

# Bot token from environment variables - check for both variable names for compatibility
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or os.environ.get('BOT_TOKEN')
if not BOT_TOKEN and not IS_RENDER:
    logger.error("Neither TELEGRAM_BOT_TOKEN nor BOT_TOKEN environment variable is set!")
    sys.exit(1)
else:
    logger.info("Bot token loaded successfully")

# API base URL from environment variables, with multiple fallbacks for compatibility
API_BASE_URL = os.environ.get('API_BASE_URL_RENDER', 'http://localhost:8000')
logger.info(f"Using API base URL: {API_BASE_URL}")

# Conversation states
# For family creation/joining
ASK_FAMILY_CODE = 1
ASK_FAMILY_NAME = 2
ASK_USER_NAME = 3
JOIN_FAMILY_CODE = 4

# For expense creation
DESCRIPTION = 10
AMOUNT = 11
SELECT_MEMBERS = 12  # For expense division
CONFIRM = 13

# For payment creation
SELECT_TO_MEMBER = 20
PAYMENT_AMOUNT = 21
PAYMENT_CONFIRM = 22

# For editing/deleting
EDIT_OPTION = 30
SELECT_EXPENSE = 31
SELECT_PAYMENT = 32
CONFIRM_DELETE = 33
EDIT_EXPENSE_AMOUNT = 34

# For listing options
LIST_OPTION = 40

# For debt adjustment
SELECT_CREDIT = 50
ADJUSTMENT_AMOUNT = 51
ADJUSTMENT_CONFIRM = 52

# Other configuration
MAX_MESSAGE_LENGTH = 4096  # Maximum message length for Telegram messages 