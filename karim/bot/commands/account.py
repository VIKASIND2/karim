from karim.bot.commands import *


@send_typing_action
def check_account(update, context):
    manager = SessionManager(update, Persistence.ACCOUNT)
    try:
        if manager.check_connection():
            # User is logged in
            client = manager.connect()
            me = client.get_me()
            username = me.username
            phone = me.phone
            client.disconnect()
            manager.discard()
            markup = CreateMarkup({Callbacks.LOGOUT: 'Log Out'}).create_markup()
            update.effective_chat.send_message(account_info.format(str(username), str(phone)), reply_markup=markup, parse_mode=ParseMode.HTML)
        else:
            # User is not logged in
            markup = CreateMarkup({Callbacks.LOGIN: 'Log In'}).create_markup()
            manager.discard()
            update.effective_chat.send_message(no_connection, reply_markup=markup, parse_mode=ParseMode.HTML)
    except:
        # Error
        manager.discard()
        update.effective_chat.send_message(problem_connecting, parse_mode=ParseMode.HTML)
        
