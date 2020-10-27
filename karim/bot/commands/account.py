from karim.bot.commands import *


@send_typing_action
@run_async
def check_account(update, context):
    if not check_auth(update, context):
        return
    instasession = InstaSession(update.effective_chat.id, update.effective_user.id)
    manager= SessionManager(Persistence.ACCOUNT, chat_id=update.effective_chat.id, user_id=update.effective_chat.id, message_id=update.message.message_id)
    message = update.effective_chat.send_message(text=checking_accounts_connection)
    try:
        if manager.check_connection():
            # User is logged in
            client = manager.connect()
            me = client.get_me()
            username = me.username
            phone = me.phone
            client.disconnect()
            manager.discard()
            text = account_info.format(str(username), str(phone))
        
            if instasession.get_creds():
                # User logged into instagram as well
                text += '\n\n' + ig_account_info.format(instasession.username, instasession.username)

            markup = CreateMarkup({Callbacks.LOGOUT: 'Log Out (Telegram)'}).create_markup()
            manager.discard()
            instasession.discard()
            context.bot.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.HTML, chat_id=update.effective_chat.id, message_id=message.id)
        else:
            # User is not logged in
            markup = CreateMarkup({Callbacks.LOGIN: 'Log In'}).create_markup()
            manager.discard()
            instasession.discard()
            context.bot.edit_message_text(no_connection, reply_markup=markup, parse_mode=ParseMode.HTML, chat_id=update.effective_chat.id, message_id=message.id)
    except:
        # Error
        manager.discard()
        instasession.discard()
        context.bot.edit_message_text(problem_connecting, parse_mode=ParseMode.HTML, chat_id=update.effective_chat.id, message_id=message.id)
        
