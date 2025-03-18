"""
Messages in English

This file contains all the texts displayed by the bot in English.
"""

class Messages:
    """Formatted messages for Telegram in English."""
    
    # Welcome messages
    WELCOME = (
        "👋 Welcome to the Family Management Bot!\n"
        "This bot helps you manage shared expenses with your family or group of friends.\n"
        "What would you like to do?"
    )
    
    MAIN_MENU = "✨ Welcome to your family dashboard!\nSelect an option:"
    
    # Error messages
    ERROR_NOT_IN_FAMILY = "❌ You're not in any family. Use /start to create or join a family."
    ERROR_FAMILY_NOT_FOUND = "❌ Family not found. It may have been deleted."
    ERROR_INVALID_OPTION = "❌ Invalid option. Please select an option from the menu."
    ERROR_API = "❌ API communication error. Please try again later."
    ERROR_INVALID_AMOUNT = "❌ Invalid amount. Please enter a positive number."
    ERROR_CREATING_EXPENSE = "❌ Error creating the expense. Please try again later."
    ERROR_MEMBER_NOT_FOUND = "❌ Your member information was not found. Please try again."
    ERROR_NO_EXPENSES = "❌ There are no registered expenses to display."
    ERROR_NO_PAYMENTS = "❌ There are no registered payments to display."
    ERROR_EXPENSE_NOT_FOUND = "❌ The specified expense was not found."
    ERROR_PAYMENT_NOT_FOUND = "❌ The specified payment was not found."
    ERROR_DELETING_EXPENSE = "❌ Error deleting the expense. Please try again later."
    ERROR_DELETING_PAYMENT = "❌ Error deleting the payment. Please try again later."
    ERROR_UPDATING_EXPENSE = "❌ Error updating the expense. Please try again later."
    
    # Success messages
    SUCCESS_FAMILY_CREATED = "✅ Family '{name}' created successfully.\n*ID:* `{id}`"
    SUCCESS_JOINED_FAMILY = "🎉 You have successfully joined the *{family_name}* family!"
    SUCCESS_EXPENSE_CREATED = "✅ Expense created successfully!"
    SUCCESS_PAYMENT_CREATED = "✅ Payment registered successfully!"
    SUCCESS_EXPENSE_DELETED = "✅ Expense deleted successfully."
    SUCCESS_PAYMENT_DELETED = "✅ Payment deleted successfully."
    SUCCESS_EXPENSE_UPDATED = "✅ Expense updated successfully."
    
    # Family creation flow messages
    CREATE_FAMILY_INTRO = "🏠 Let's create a new family.\n\n" \
                         "What will your family be called?"
    
    CREATE_FAMILY_NAME_RECEIVED = "👍 Family name received: *{family_name}*\n\n" \
                                 "Now, what's your name? This is how other members will identify you."
    
    # Join family flow messages
    JOIN_FAMILY_INTRO = "🔗 Let's join an existing family.\n\n" \
                       "Please enter the ID of the family you want to join:"
    
    JOIN_FAMILY_NAME_PROMPT = "👍 Valid family code.\n\n" \
                             "What's your name? This is how other members will identify you."
    
    JOIN_FAMILY_SUCCESS = "✅ You have successfully joined the *{family_name}* family!"
    
    # Expense flow messages
    CREATE_EXPENSE_INTRO = "💸 Let's create a new expense.\n\n" \
                          "What's the description of the expense? (e.g., Supermarket, Dinner, etc.)"
    
    CREATE_EXPENSE_AMOUNT = "👍 Description received: *{description}*\n\n" \
                           "Now, what's the amount of the expense? (e.g., 100.50)"
    
    CREATE_EXPENSE_DIVISION = "👍 Amount received: *${amount:.2f}*\n\n" \
                             "How do you want to split this expense?"
    
    CREATE_EXPENSE_SELECT_MEMBERS = "👥 Select the members who will share this expense:\n\n" \
                                   "Press a name to select/deselect\n" \
                                   "- Names with ✅ are selected\n" \
                                   "- Names with ⬜ are not selected\n\n" \
                                   "When you're done, press \"✓ Continue\""
    
    CREATE_EXPENSE_CONFIRM = "📝 Expense summary:\n\n" \
                            "*Description:* {description}\n" \
                            "*Amount:* ${amount:.2f}\n" \
                            "*Paid by:* {paid_by}\n" \
                            "*Shared among:* {split_among}\n\n" \
                            "Do you confirm this expense?"
    
    # Messages for listing expenses
    EXPENSES_LIST_HEADER = "📋 *Expense List*\n\n"
    
    EXPENSE_LIST_ITEM = (
        "*Description:* {description}\n"
        "*Amount:* {amount}\n"
        "*Paid by:* {paid_by}\n"
        "*Date:* {date}\n"
        "----------------------------\n\n"
    )
    
    # Messages for listing payments
    PAYMENTS_LIST_HEADER = "💳 *Payment List*\n\n"
    
    PAYMENT_LIST_ITEM = (
        "*From:* {from_member}\n"
        "*To:* {to_member}\n"
        "*Amount:* {amount}\n"
        "*Date:* {date}\n"
        "----------------------------\n\n"
    )
    
    # Messages for expenses and payments not found
    NO_EXPENSES = "📋 There are no registered expenses in this family."
    NO_PAYMENTS = "💳 There are no registered payments in this family."
    
    # Payment flow messages
    CREATE_PAYMENT_INTRO = "💳 Let's register a new payment.\n\n" \
                          "Who are you paying?"
    
    NO_DEBTS = "✅ *Congratulations!* At this moment, you don't have any pending debts with any family member."
    
    SELECT_PAYMENT_RECIPIENT = "💳 Who do you want to pay? Select a family member you owe money to:"
    
    CREATE_PAYMENT_AMOUNT = "👍 Selected recipient: *{to_member}*\n\n" \
                           "Now, what's the payment amount? (e.g., 100.50)"
    
    CREATE_PAYMENT_CONFIRM = "📝 Payment summary:\n\n" \
                            "*From:* {from_member}\n" \
                            "*To:* {to_member}\n" \
                            "*Amount:* ${amount:.2f}\n\n" \
                            "Do you confirm this payment?"
    
    # Edit/delete messages
    EDIT_OPTIONS = "✏️ What do you want to do?"
    
    SELECT_EXPENSE_TO_EDIT = "📝 Select the expense you want to edit:"
    SELECT_EXPENSE_TO_DELETE = "🗑️ Select the expense you want to delete:"
    
    SELECT_PAYMENT_TO_EDIT = "📝 Select the payment you want to edit:"
    SELECT_PAYMENT_TO_DELETE = "🗑️ Select the payment you want to delete:"
    
    CONFIRM_DELETE_EXPENSE = "⚠️ Are you sure you want to delete this expense?\n\n{details}"
    CONFIRM_DELETE_PAYMENT = "⚠️ Are you sure you want to delete this payment?\n\n{details}"
    
    EDIT_EXPENSE_AMOUNT = "📝 Enter the new amount for the expense:\n\n{details}"
    
    # Additional messages for editing/deleting
    INVALID_EDIT_OPTION = "❌ Invalid edit option. Please select an option from the menu."
    NO_EXPENSES_TO_EDIT = "❌ There are no registered expenses to edit."
    NO_EXPENSES_TO_DELETE = "❌ There are no registered expenses to delete."
    NO_PAYMENTS_TO_DELETE = "❌ There are no registered payments to delete."
    NO_PAYMENTS_TO_EDIT = "❌ There are no registered payments to edit."
    ITEM_NOT_FOUND = "❌ The selected item was not found."
    
    # General messages
    CANCEL_OPERATION = "❌ Operation cancelled."
    LOADING = "⏳ Loading..."
    FAMILY_INFO = "ℹ️ *Family Information*\n\n*Name:* {name}\n*Family ID:* `{id}`\n*Members:* {members_count}\n\n*Members:*\n{members_list}"
    FAMILY_INVITATION = "🔗 *Family Invitation*\n\n*Name:* {name}\n*ID:* `{id}`\n\nShare this ID with the people you want to invite to your family."
    UNKNOWN_COMMAND = "I don't understand that command. Here's the main menu:"
    
    # Messages for balances
    BALANCES_HEADER = "💰 *Family Balances*\n\n"
    
    # Balance formatting elements
    BALANCE_NET = "Net balance"
    BALANCE_TOTAL_FAVOR = "Total in your favor"
    BALANCE_TOTAL_DEBT = "Total debt"
    BALANCE_DEBTS = "Debts"
    BALANCE_CREDITS = "Credits"
    BALANCE_NO_DEBT = "Doesn't owe anyone"
    BALANCE_NO_CREDIT = "No one owes them"
    
    BALANCE_SUMMARY = "\n\n📊 *Your balance summary:*\n"
    YOU_OWE = "💸 *You owe:* ${amount:.2f} in total\n"
    OWE_TO = "└ To {name}: ${amount:.2f}\n"
    LARGEST_DEBT = "└ Largest debt to {name}: ${amount:.2f}\n"
    NO_DEBT = "💸 *You don't owe money to anyone*\n"
    OWED_TO_YOU = "💰 *Owed to you:* ${amount:.2f} in total\n"
    FROM_USER = "└ {name}: ${amount:.2f}\n"
    LARGEST_CREDIT = "└ Largest credit from {name}: ${amount:.2f}\n"
    NO_CREDIT = "💰 *No one owes you money*\n"
    
    # Messages for sharing invitation
    SHARE_INVITATION_INTRO = "🔗 Share this link to invite someone to join your family:"
    
    SHARE_INVITATION_ID = "📝 Family ID: `{family_id}`\n\nShare this ID with whoever you want to join your family."
    
    SHARE_INVITATION_QR = "They can also scan this QR code:"
    
    # Message for invitation link
    INVITATION_LINK = (
        "🔗 *Family Invitation*\n\n"
        "Share this QR code or the following link to invite someone to join your family:\n\n"
        "`{invite_link}`\n\n"
        "Instructions for the invitee:\n"
        "1. Click on the link or scan the QR code\n"
        "2. The bot will open\n"
        "3. Press the 'START' button or send /start\n"
        "4. You will be automatically added to the family"
    )
    
    # Messages specific to the language system
    LANGUAGE_SELECTION = "🌍 Select your preferred language:"
    LANGUAGE_UPDATED = "✅ Language updated to English!"
    
    # Messages for keyboards
    KB_VIEW_BALANCES = "💰 View Balances"
    KB_CREATE_EXPENSE = "💸 Create Expense"
    KB_LIST_RECORDS = "📜 List Records"
    KB_REGISTER_PAYMENT = "💳 Register Payment"
    KB_EDIT_DELETE = "✏️ Edit/Delete"
    KB_FAMILY_INFO = "ℹ️ Family Info"
    KB_SHARE_INVITATION = "🔗 Share Invitation"
    KB_CHANGE_LANGUAGE = "🌍 Change Language"
    KB_EDIT_EXPENSES = "📝 Edit Expenses"
    KB_DELETE_EXPENSES = "🗑️ Delete Expenses"
    KB_EDIT_PAYMENTS = "📝 Edit Payments"
    KB_DELETE_PAYMENTS = "🗑️ Delete Payments"
    KB_BACK_TO_MENU = "↩️ Back to Menu"
    KB_CREATE_FAMILY = "🏠 Create Family"
    KB_JOIN_FAMILY = "🔗 Join Family"
    KB_CONFIRM = "✅ Confirm"
    KB_CANCEL = "❌ Cancel"
    KB_LIST_EXPENSES = "📋 List Expenses"
    KB_LIST_PAYMENTS = "📊 List Payments"
    
    # Messages for listing records
    LIST_RECORDS_TITLE = "📜 *List Records*\n\n"
    WHAT_RECORDS_TO_VIEW = "Which records would you like to view?"
    ERROR_LISTING_OPTIONS = "Error displaying listing options. Please try again."
    ERROR_PROCESSING_OPTION = "Error processing the selected option. Please try again."
    
    # Messages for balances
    BALANCES_HEADER = "💰 *Family Balances*\n\n"
    BALANCE_SUMMARY = "\n\n📊 *Your balance summary:*\n"
    YOU_OWE = "💸 *You owe:* ${amount:.2f} in total\n"
    OWE_TO = "└ To {name}: ${amount:.2f}\n"
    LARGEST_DEBT = "└ Largest debt to {name}: ${amount:.2f}\n"
    NO_DEBT = "💸 *You don't owe money to anyone*\n"
    OWED_TO_YOU = "💰 *Owed to you:* ${amount:.2f} in total\n"
    FROM_USER = "└ {name}: ${amount:.2f}\n"
    LARGEST_CREDIT = "└ Largest credit from {name}: ${amount:.2f}\n"
    NO_CREDIT = "💰 *No one owes you money*\n" 