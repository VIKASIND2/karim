from karim.bot.commands import *
from karim.bot.commands.signin import client_sign_in
from karim.modules import sheet

def start(update, context):
    """
    Subscribe the user to the newsletter.
    Adds user id to Sheet Mailing List
    """
    users = secrets.get_var('USERS')
    print('USERS: ', users)
    if update.effective_user.id in users:
        # User is Admin, start sign in
        client_sign_in(update, context)
    elif sheet.is_subscriber(update.effective_user.id):
        # User is already subscribed
        update.message.reply_text(already_subscribed_text)
        return
    else:
        # Subscribe user
        result = sheet.add_subscriber(update.effective_user.id)
        if result:
            update.message.reply_text(subscription_successful_text)
            return
        else:
            update.message.reply_text(error_in_subscribing_text)
            return


