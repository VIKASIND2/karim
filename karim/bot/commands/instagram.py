from instaclient.errors.common import InvalidUserError, PrivateAccountError
from karim.bot.commands import *
from karim import instaclient

@run_async
@send_typing_action
def ig_login(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END
    
    instasession:InstaSession = InstaSession(update.effective_chat.id, update.effective_user.id)
    message = update.effective_chat.send_message(text=checking_ig_status)
    instasession.set_message(message.message_id)
    result = instaclient.check_status()
    if result:
        # Account is already logged in
        context.bot.edit_message_text(text=user_logged_in_text, chat_id=instasession.chat_id, message_id=message.message_id)
        return ConversationHandler.END

    else:
        # Request Username
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        context.bot.edit_message_text(text=input_ig_username_text, chat_id=instasession.chat_id, message_id=message.message_id, reply_markup=markup)
        return InstaStates.INPUT_USERNAME

    
@run_async
@send_typing_action
def input_username(update, context):
    instasession:InstaSession = InstaSession.deserialize(Persistence.INSASESSION, update)
    if not instasession:
        return InstaStates.INPUT_USERNAME
    
    username = update.message.text 
    message = update.message.reply_text(text=checking_user_vadility_text)
    instasession.set_message(message.message_id)
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    # Verify User
    try:
        instaclient.is_valid_user(username)
    except InvalidUserError as error:
        
        context.bot.edit_message_text(text=invalid_user_text.format(error.username), chat_id=update.effective_chat.id, message_id=instasession.message_id, reply_markup=markup)
        instasession.set_message(message.message_id)
        return InstaStates.INPUT_USERNAME
    except PrivateAccountError as error:
        pass
    instasession.set_username(username)
    # Request Password
    context.bot.edit_message_text(text=input_password_text, chat_id=update.effective_chat.id, message_id=instasession.message_id, reply_markup=markup)
    return InstaStates.INPUT_PASSWORD


@run_async
@send_typing_action
def input_password(update, context):
    instasession:InstaSession = InstaSession.deserialize(Persistence.INSASESSION, update)
    if not instasession:
        return InstaStates.INPUT_USERNAME
    



@run_async
@send_typing_action
def cancel_instagram(update, context, instasession:InstaSession=None):
    if not instasession:
        instasession = InstaSession.deserialize(Persistence.INSASESSION, update)
        if not instasession:
            return

    try:
        update.callback_query.edit_message_text(text=cancelled_instagram_text)
    except:
        try:
            context.bot.edit_message_text(chat_id=instasession.chat_id, message_id=instasession.message_id, text=cancelled_instagram_text)
        except:
            update.effective_chat.send_message(text=cancelled_instagram_text)
    instasession.discard()
    return ConversationHandler.END

    
    






