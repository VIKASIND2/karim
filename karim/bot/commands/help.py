from karim.bot import *

def help(update, context):
    update.message.chat.send_message(text=help_text, parse_mode=ParseMode.HTML)