from karim.bot.commands import *

@run_async
def help_def(update, context):
    print('ID: ', update.effective_user.id)
    update.message.chat.send_message(text=help_text, parse_mode=ParseMode.HTML)