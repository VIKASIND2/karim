from karim.bot import *
from karim.bot.texts import *
from karim.classes.persistence import Persistence
from karim.classes.session_manager import SessionManager
from karim.classes.forwarder import Forwarder
from telethon.sync import TelegramClient



def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


def create_menu(button_titles, callbacks, cols=1):
    print("BOT: menu()")
    keyboard = []
    index = 0
    row = []
    for title in button_titles:
        keyboard_button = InlineKeyboardButton(
            title, callback_data=callbacks[index])
        if len(row) < cols:
            row.append(keyboard_button)
        else:
            keyboard.append(row)
            row = []
            row.append(keyboard_button)
        index += 1
    if row != "":
        keyboard.append(row)
    markup = InlineKeyboardMarkup(keyboard)
    return markup

