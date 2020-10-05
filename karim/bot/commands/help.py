from karim.bot.commands import *

@run_async
def help_def(update, context):
    update.message.chat.send_message(text=help_text, parse_mode=ParseMode.HTML)