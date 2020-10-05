import time
import threading
from telethon.errors.rpcerrorlist import PasswordHashInvalidError, PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError, SessionPasswordNeededError
from karim.secrets import secrets
from karim.bot.commands import *
import re

@run_async
@send_typing_action
def client_sign_in(update, context):
    """Initializes the bot and sign into the Telegram Client. Walks the user through a wizard, asking to input Telegram phone number, password and security code to sign into the client."""
    # Check if user is already signed in
    manager = SessionManager(update, Persistence.SIGNIN)
    result =  manager.check_connection()
    if result:
        # User is already authorised
        message = update.effective_chat.send_message(client_already_signed_in, parse_mode = ParseMode.HTML)
        manager.discard()
        return ConversationHandler.END
    elif not result:
        # Request Phone Number Input from user
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = update.effective_chat.send_message(request_phone_text, parse_mode = ParseMode.HTML, reply_markup = markup)
        manager.set_message(message)
        return StartStates.INPUT_PHONE
    else:
        # Error
        update.effective_chat.send_message(error_checking_connection, parse_mode=ParseMode.HTML)
        return ConversationHandler.END


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
    

@run_async
@send_typing_action
def input_phone(update, context):
    """Input Telegram phone number to log into the Telegram client"""
    manager = Persistence.deserialize(Persistence.SIGNIN, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    phone = update.message.text
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    if not validNumber(phone):
        # Phone number is not valid, try again
        message = update.message.reply_text(phone_not_valid, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return
    # Phone is valid
    manager.set_phone(phone)

    # REQUEST CODE & MANAGE ERRORS
    return manage_code_request(update, context, request_code_text, manager)
    

@run_async
@send_typing_action
def input_code(update, context):
    """Input Telegram security code to log into the Telegram client"""
    manager: SessionManager = Persistence.deserialize(Persistence.SIGNIN, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    code = update.message.text
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    manager.set_code(code)
    # ATTEMPT SIGN IN (No Password)
    try:
        # SIGN IN
        manager.sign_in()
        update.message.reply_text(client_signing_successful, parse_mode=ParseMode.HTML)
        manager.discard()
        return ConversationHandler.END

    except PhoneCodeInvalidError:
        # INVALID CODE - TRY AGAIN
        message = update.message.reply_text(invalid_security_code, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return StartStates.INPUT_CODE

    except PhoneCodeExpiredError:
        print('Code Expired')
        # CODE EXPIRED; SEND CODE AGAIN
        return manage_code_request(update, context, code_expired, manager)

    except SessionPasswordNeededError:
        # REQUEST PASSWORD
        message = update.message.reply_text(request_password_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return StartStates.INPUT_PASSWORD

    except:
        # SIGN IN FAILED
        update.message.reply_text(failed_client_signin, parse_mode=ParseMode.HTML)
        cancel_start(update, context, include_message=False)
        return ConversationHandler.END   


@run_async
@send_typing_action
def input_password(update, context):
    """Input Telegram password to log into the Telegram client"""
    manager: SessionManager = Persistence.deserialize(Persistence.SIGNIN, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    password = update.message.text
    manager.set_password(password)

    # ATTEMPT SIGN IN
    # SIGN IN
    try:
        manager.sign_in(password=True)
        update.message.reply_text(client_signing_successful, parse_mode=ParseMode.HTML)
        manager.discard()
        return ConversationHandler.END
    except PasswordHashInvalidError:
        # Password is wrong, ask again
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = update.message.reply_text(wrong_password_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return StartStates.INPUT_PASSWORD
    except:
        # Attempt Another Sign In after 15 seconds
        time.sleep(5)
        try:
            manager.sign_in(password=True)
            update.message.reply_text(client_signing_successful, parse_mode=ParseMode.HTML)
            manager.discard()
            return ConversationHandler.END
        except:
            # SIGN IN FAILED
            update.message.reply_text(failed_client_signin, parse_mode=ParseMode.HTML)
            cancel_start(update, context, include_message=False)
            return ConversationHandler.END   


@run_async
def cancel_start(update, context, include_message=True):
    """Fallback method. Cancels Start manager"""
    manager = Persistence.deserialize(Persistence.SIGNIN, update)
    if not manager:
        # Another user tried to enter the conversation
        return
    if include_message:
        if update.callback_query is not None:
            update.callback_query.edit_message_text('Sign In Cancelled')
        else:
            update.effective_chat.send_message('Sign In Cancelled')
    manager.discard()
    return ConversationHandler.END


def manage_code_request(update, context, text, manager):
    # SEND AND REQUEST SECURITY CODE
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    try:
        manager.request_code()
        # Request Security Code Input
        message = update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message)
        return StartStates.INPUT_CODE

    except FloodWaitError:
        # CODE SENT TOO MANY TIMES
        # Ask to input last sent code
        update.message.reply_text(floodwaiterror_text, parse_mode=ParseMode.HTML)
        return StartStates.INPUT_CODE

    except:
        # CODE REQUEST FAILED
        update.message.reply_text(requestcodefailed_text, parse_mode=ParseMode.HTML)
        cancel_start(update, context)
        return ConversationHandler.END
