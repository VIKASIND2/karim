from karim.bot import *
from karim.bot.texts import *
from karim.classes.persistence import Persistence
from karim.classes.session_manager import SessionManager
from karim.classes.forwarder import Forwarder
from karim.classes.forwarder_markup import ForwarderMarkup, CreateMarkup, MarkupDivider
from telethon.sync import TelegramClient



def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func

