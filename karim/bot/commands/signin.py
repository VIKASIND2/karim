from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, FloodWaitError
from karim.secrets import secrets
from karim.bot.commands import *
import re

def client_sign_in(update, context):
    """Initializes the bot and sign into the Telegram Client. Walks the user through a wizard, asking to input Telegram phone number, password and security code to sign into the client."""
    # Check if user is already signed in
    manager = SessionManager(update)
    if manager.connect() is None:
        # User is already authorised
        message = update.effective_chat.send_message(client_already_signed_in, parse_mode = ParseMode.HTML)
        return ConversationHandler.END
    else:
        # Request Phone Number Input from user
        markup = create_menu(['Cancel'], [Callbacks.CANCEL])
        message = update.effective_chat.send_message(request_phone_text, parse_mode = ParseMode.HTML, reply_markup = markup)
        manager.set_message(message)
        return StartStates.INPUT_PHONE


def validNumber(phone_number):
    """Checks if a phone number is in a valid format. Does not check weather the provided phone number is connected to a real Telegram account"""
    # 1) Begins with 0 or 91 
    # 2) Then contains 7 or 8 or 9. 
    # 3) Then contains 9 digits 
    phone_number.strip()
    if phone_number[0] is '+':
        phone_number = phone_number[1:]
    Pattern = re.compile("(0/91)?[1-9][0-9]{9}") 
    return Pattern.match(phone_number) 
    

def input_phone(update, context):
    """Input Telegram phone number to log into the Telegram client"""
    manager = Persistence.load_pkl(Persistence.ATTEMPT, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    phone = update.message.text
    markup = create_menu(['Cancel'], [Callbacks.CANCEL])
    if not validNumber(phone):
        # Phone number is not valid, try again
        message = update.message.reply_text(phone_not_valid, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return
    # Phone is valid
    manager.set_phone(phone)

    # Request Password input to log in
    message = update.message.reply_text(request_password_text, reply_markup=markup, parse_mode=ParseMode.HTML)
    manager.set_message(message)
    return StartStates.INPUT_PASSWORD


def input_password(update, context):
    """Input Telegram password to log into the Telegram client"""
    manager = Persistence.load_pkl(Persistence.ATTEMPT, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    password = update.message.text
    markup = create_menu(['Cancel'], [Callbacks.CANCEL])
    manager.set_password(password)

    # Send Security Code
    result = manager.request_code()
    if result is FloodWaitError:
        print('FloodWaitError')
        update.message.reply_text(floodwaiterror_text, parse_mode=ParseMode.HTML)
        cancel_start(update, context)
        return ConversationHandler.END

    elif result is not None:
        print('Code Request Failed')
        text = requestcodefailed_text + ' {}'.format(result)
        update.message.reply_text(text, parse_mode=ParseMode.HTML)
        cancel_start(update, context)
        return ConversationHandler.END

    else:
        # Request Security Code Input
        message = update.message.reply_text(request_code_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return StartStates.INPUT_CODE


def input_code(update, context):
    """Input Telegram security code to log into the Telegram client"""
    manager = Persistence.load_pkl(Persistence.ATTEMPT, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    code = update.message.text
    markup = create_menu(['Cancel'], [Callbacks.CANCEL])
    manager.set_code(code)
    # manager Sign In
    response = manager.sign_in()
    if response is PhoneCodeInvalidError:
        # Sign In Failed
        print('Sign In Failed')
        manager.request_code()
        message = update.message.reply_text(invalid_security_code, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return StartStates.INPUT_CODE
    if response is not None:
        print('Sign In Failed')
        update.message.reply_text(failed_client_signin, reply_markup=markup, parse_mode=ParseMode.HTML)
        cancel_start(update, context)
    else:
        print('Sign In Successful')
        update.message.reply_text(client_signing_successful, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.delete_pkl()
        return ConversationHandler.END


def cancel_start(update, context):
    """Fallback method. Cancels Start manager"""
    manager = Persistence.load_pkl(Persistence.ATTEMPT, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    if update.callback_query is not None:
        update.callback_query.edit_message_text('Sign In Cancelled')
    else:
        update.effective_chat.send_message('Sign In Cancelled')
    manager.delete_pkl()
    return ConversationHandler.END