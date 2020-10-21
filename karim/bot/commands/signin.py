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
    if not check_auth(update, context):
        return ConversationHandler.END
    # Check if user is already signed in
    try:
        manager = SessionManager(Persistence.SIGNIN, chat_id=update.effective_chat.id, user_id=update.effective_chat.id, message_id=update.message.message_id)
    except AttributeError as error:
        manager = SessionManager(Persistence.SIGNIN, chat_id=update.effective_chat.id, user_id=update.effective_chat.id, message_id=update.callback_query.inline_message_id
)
    result =  manager.check_connection()
    if result:
        # User is authorised
        message = update.effective_chat.send_message(client_already_signed_in, parse_mode = ParseMode.HTML)
        manager.discard()
        return ConversationHandler.END
    elif not result:
        # Request Phone Number Input from user
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        try:
            message = update.callback_query.edit_message_text(request_phone_text, parse_mode=ParseMode.HTML, reply_markup=markup)
        except:
            message = update.effective_chat.send_message(request_phone_text, parse_mode = ParseMode.HTML, reply_markup = markup)
        manager.set_message(message.message_id)
        return LogInStates.INPUT_PHONE
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
    if phone_number[0] == '+':
        phone_number = phone_number[1:]
    Pattern = re.compile("(0/91)?[1-9][0-9]{9}") 
    return Pattern.match(phone_number) 
    

@run_async
@send_typing_action
def input_phone(update, context):
    """Input Telegram phone number to log into the Telegram client"""
    print('received phone')
    manager = dict_to_obj(Persistence.deserialize(Persistence.SIGNIN, update), method=Objects.SESSION_MANAGER)
    if not manager:
        # Another user tried to enter the conversation
        print('FAILED ATTEMPT AT PERSISTENCE')
        return
    phone = update.message.text
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel', Callbacks.REQUEST_CODE: 'Resend Code'}).create_markup()
    if not validNumber(phone):
        # Phone number is not valid, try again
        message = update.message.reply_text(phone_not_valid, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message.message_id)
        return
    # Phone is valid
    manager.set_phone(phone)

    # REQUEST CODE & MANAGE ERRORS
    return manage_code_request(update, context, request_code_text, manager, markup)
    

@run_async
@send_typing_action
def input_code(update, context):
    """Input Telegram security code to log into the Telegram client"""
    manager: SessionManager = dict_to_obj(Persistence.deserialize(Persistence.SIGNIN, update), method=Objects.SESSION_MANAGER)
    if not manager:
        # Another user tried to enter the conversation
        print('FAILED ATTEMPT AT PERSISTENCE')
        return
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel', Callbacks.REQUEST_CODE: 'Resend Code'}).create_markup()
    if update.callback_query is not None:
        if update.callback_query.data == Callbacks.REQUEST_CODE:
            update.callback_query.answer()
            return manage_code_request(update, context, resend_code_text, manager, markup, try_again=True)
        elif update.callback_query == Callbacks.CANCEL:
            update.callback_query.answer()
            return cancel_start(update, context)

    code = update.message.text
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
        manager.set_message(message.message_id)
        return LogInStates.INPUT_CODE

    except PhoneCodeExpiredError:
        print('Code Expired')
        # CODE EXPIRED; SEND CODE AGAIN
        return manage_code_request(update, context, code_expired, manager, markup)

    except SessionPasswordNeededError:
        # REQUEST PASSWORD
        message = update.message.reply_text(request_password_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        manager.set_message(message.message_id)
        return LogInStates.INPUT_PASSWORD

    except:
        # SIGN IN FAILED
        update.message.reply_text(failed_client_signin, parse_mode=ParseMode.HTML)
        cancel_start(update, context, include_message=False)
        return ConversationHandler.END   


@run_async
@send_typing_action
def input_password(update, context):
    """Input Telegram password to log into the Telegram client"""
    manager: SessionManager = dict_to_obj(Persistence.deserialize(Persistence.SIGNIN, update), method=Objects.SESSION_MANAGER)
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
        manager.set_message(message.message_id)
        return LogInStates.INPUT_PASSWORD
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
    manager = dict_to_obj(Persistence.deserialize(Persistence.SIGNIN, update), method=Objects.SESSION_MANAGER)
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


def manage_code_request(update, context, text, manager: SessionManager, markup=None, try_again=False):
    # SEND AND REQUEST SECURITY CODE
    try:
        manager.request_code()
        # Request Security Code Input
        if markup is not None:
            reply_markup = markup
        else:
            reply_markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        try:
            message = update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            manager.set_message(message.message_id)
        except:
            try:
                message = update.callback_query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                manager.set_message(message.message_id)
            except: pass
        return LogInStates.INPUT_CODE

    except FloodWaitError as error:
        print('Error in singin.manage_code_request(): ', error)
        # CODE SENT TOO MANY TIMES
        # Ask to input last sent code
        try:
            update.message.reply_text(floodwaiterror_text, parse_mode=ParseMode.HTML)
        except:
            update.callback_query.edit_message_text(floodwaiterror_text, parse_mode=ParseMode.HTML)
        return LogInStates.INPUT_CODE

    except Exception as error:
        print('Error in singin.manage_code_request(): ', error)
        # CODE REQUEST FAILED
        try:
            update.message.reply_text(requestcodefailed_text, parse_mode=ParseMode.HTML)
        except:
            update.callback_query.edit_message_text(requestcodefailed_text, parse_mode=ParseMode.HTML)
        cancel_start(update, context)
        return ConversationHandler.END
