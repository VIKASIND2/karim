from karim.bot.commands import *
from karim.bot.commands.signin import client_sign_in
from karim.modules import sheet

def start_newsletter(update, context):
    """
    Subscribe the user to the newsletter.
    Adds user id to Sheet Mailing List
    """
    users = list(secrets.get_var('USERS'))
    if update.effective_user.id in users:
        # User is Admin, start sign in
        return client_sign_in(update, context)

    message = update.effective_chat.send_message(checking_subscription)
    subscribed = sheet.is_subscriber(update.effective_user.id)
    if subscribed :
        # User is already subscribed
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=already_subscribed_text)
        return
    else:
        # Subscribe user
        result = sheet.add_subscriber(update.effective_user.id)
        if result:
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=subscription_successful_text)
            return
        else:
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=error_in_subscribing_text)
            return


