from karim.bot.commands import *

@run_async
@send_typing_action
def instagram_log_out(update, context):
    if check_auth(update, context):
        from karim import instaclient 
        instasession = InstaSession(update.effective_chat.id, update.effective_user.id)
        instasession.delete_creds()
        instasession.discard()
        # User is authorised
        if update.callback_query:
            message = update.callback_query.edit_message_text(text=logging_out)
        else:
            update.message.delete()
            message = update.effective_chat.send_message(text=logging_out)
        result = instaclient.logout()
        if result:
            message.edit_text(text=instagram_loggedout_text)
        else:
            message.edit_text(text=error_loggingout_text)
    else:
        update.effective_chat.send_message(text=not_admin_text)

