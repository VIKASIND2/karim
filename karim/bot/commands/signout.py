from karim.bot.commands import *

@run_async
@send_typing_action
def sign_out(update, context):
    try:
        manager = SessionManager(Persistence.SIGNOUT, chat_id=update.effective_chat.id, user_id=update.effective_chat.id, message_id=update.message.message_id)
    except AttributeError as error:
        manager = SessionManager(Persistence.SIGNOUT, chat_id=update.effective_chat.id, user_id=update.effective_chat.id, message_id=update.callback_query.inline_message_id)
    result = manager.check_connection()
    if result:
        # User is logged in
        markup = CreateMarkup({Callbacks.LOGOUT: 'Yes, Sign Out', Callbacks.CANCEL: 'Cancel'}).create_markup()
        if update.callback_query is None:
            message = update.effective_chat.send_message(confirm_sign_out_text, reply_markup=markup)
            manager.set_message(message.message_id)
        else:
            message = update.callback_query.edit_message_text(confirm_sign_out_text, reply_markup=markup)
            manager.set_message(message.message_id)
        return LogOutStates.CONFIRM
    elif not result:
        # User is not logged in
        try:
            manager.sign_out()
        except:
            pass
        update.effective_chat.send_message(not_signed_in, parse_mode=ParseMode.HTML)
        manager.discard()
        return ConversationHandler.END
    else:
        # Error
        update.effective_chat.send_message(error_checking_connection, parse_mode=ParseMode.HTML)
        manager.discard()
        return ConversationHandler.END


@run_async
@send_typing_action
def confirm_sign_out(update, context):
    manager = dict_to_obj(SessionManager.deserialize(SessionManager.SIGNOUT, update), method=Objects.SESSION_MANAGER)
    if not manager:
        # Another user tried to enter the conversation
        return
    
    data = update.callback_query.data
    if data == Callbacks.LOGOUT:
        if manager.sign_out():
            # Log Out Successful
            context.bot.edit_message_text(chat_id=manager.chat_id, message_id=manager.message_id, text=sign_out_successful, parse_mode=ParseMode.HTML)
        else:
            # Error in Log Out 
            context.bot.edit_message_text(chat_id=manager.chat_id, message_id=manager.message_id, text=sign_out_unsuccessful, parse_mode=ParseMode.HTML)
        manager.discard()
        return ConversationHandler.END
    else:
        return cancel_sign_out(update, context)


@run_async
def cancel_sign_out(update, context):
    manager:SessionManager = dict_to_obj(SessionManager.deserialize(SessionManager.SIGNOUT, update), method=Objects.SESSION_MANAGER)
    if not manager:
        # Another user tried to enter the conversation
        return
    if update.callback_query is None:
        update.effective_chat.send_message(sign_out_cancelled, parse_mode=ParseMode.HTML)
    else:
        update.callback_query.edit_message_text(sign_out_cancelled, parse_mode=ParseMode.HTML)
    manager.discard()
    return ConversationHandler.END


        
