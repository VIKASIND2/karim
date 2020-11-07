from karim.bot.commands import *

@run_async
def help_def(update, context):
    update.message.chat.send_message(text=help_text, parse_mode=ParseMode.HTML)

def admin_help(update, context):
    if check_auth(update, context):
        update.message.chat.send_message(text=admin_help_text, parse_mode=ParseMode.HTML)