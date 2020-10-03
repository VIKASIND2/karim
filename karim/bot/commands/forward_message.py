# TODO: Select Groups
# TODO: Select Message
# TODO: Retrieve Group Members
# TODO: Send Message
from telethon.errors.rpcbaseerrors import UnauthorizedError
from karim.bot.commands import *

def forward_message(update, context):
    """Initialize message Conversation"""
    forwarder = Forwarder(update)
    result = forwarder.check_connection()
    if not result:
        # User is authorised
        # Get Group List
        try:
            # Get Groups
            groups = forwarder.get_dialogues()
            forwarder.set_groups(groups)
            # Create Markup

        except UnauthorizedError:
            # User is not logged in
            update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
            cancel_forward(update, context)
            return ConversationHandler.END
        except:
            update.message.reply_text(failed_get_dialogues, parse_mode=ParseMode.HTML)
            cancel_forward(update, context)
            return ConversationHandler.END
    



def select_group(update, context):
    """Select group(s) to send the message to"""



def cancel_forward(update, context):
    forwarder = Persistence.load_pkl(Persistence.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return
    if update.callback_query is not None:
        update.callback_query.edit_message_text('Message Forward Cancelled')
    else:
        update.effective_chat.send_message('Message Forward Cancelled')
    forwarder.delete_pkl()
    return ConversationHandler.END
    