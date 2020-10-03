# TODO: Select Groups
# TODO: Select Message
# TODO: Retrieve Group Members
# TODO: Send Message
from telethon.errors.rpcbaseerrors import UnauthorizedError
from karim.bot.commands import *


def forward_message(update, context):
    """Initialize Forwarder Conversation. Ask for message input"""
    forwarder = Forwarder(update)
    result = forwarder.check_connection()
    if not result:
        # User is authorised
        # Ask for message text
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        forwarder.set_message(update.effective_chat.send_message(send_message_to_forward, reply_markup=markup, parse_mode=ParseMode.HTML))            
        return MessageStates.SELECT_GROUP
    else:
        # User is not logged in
        update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
        cancel_forward(update, context)
        return ConversationHandler.END


def select_message(update, context):
    """Initialize message Conversation"""
    forwarder: Forwarder = Forwarder.load_pkl(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return
    # Set Forwarder Message
    forwarder.set_text(update.message.text)

    # SEND GROUP SELECTION
    # Check User Connection to the Client
    result = forwarder.check_connection()
    if not result:
        # User is authorised
        # Get Group List
        try:
            # Get Groups
            groups = forwarder.get_dialogues()
            forwarder.set_groups(groups)
            # Create Markup
            markup = ForwarderMarkup(forwarder)
            reply_markup = markup.create_markup()
            # Send Message
            forwarder.set_message(update.effective_chat.send_message(select_group_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML))
            return MessageStates.CONFIRM
        except UnauthorizedError:
            # User is not logged in
            update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
            cancel_forward(update, context)
            return ConversationHandler.END
        except:
            update.message.reply_text(failed_get_dialogues, parse_mode=ParseMode.HTML)
            cancel_forward(update, context)
            return ConversationHandler.END
    else:
        # User is not logged in
        update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
        cancel_forward(update, context)
        return ConversationHandler.END

    
def select_group(update, context):
    forwarder: Forwarder = Forwarder.load_pkl(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return

    # GET INPUT CALLBACK 
    data = update.callback_query.data
    if data is Callbacks.CANCEL:
        # CANCEL
        print('Cancel')
    elif data is Callbacks.DONE:
        # DONE
        print('Done')
    elif data is Callbacks.NONE:
        # Markup Divider: Do Nothing
        return
    elif data is Callbacks.LEFT:
        print('Left')
        # Rotate Shown Groups Left
    elif data is Callbacks.RIGHT:
        print('Right')

    # SEND GROUP SELECTION
    # Check User Connection to the Client
    result = forwarder.check_connection()
    if not result:
        # User is authorised
        # Get Group List
        try:
            # Get Groups
            groups = forwarder.get_dialogues()
            forwarder.set_groups(groups)
            # Create Markup
            markup = ForwarderMarkup(forwarder)
            reply_markup = markup.create_markup()
            # Send Message
            forwarder.set_message(update.effective_chat.send_message(select_group_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML))
            return MessageStates.CONFIRM
        except UnauthorizedError:
            # User is not logged in
            update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
            cancel_forward(update, context)
            return ConversationHandler.END
        except:
            update.message.reply_text(failed_get_dialogues, parse_mode=ParseMode.HTML)
            cancel_forward(update, context)
            return ConversationHandler.END
    else:
        # User is not logged in
        update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
        cancel_forward(update, context)
        return ConversationHandler.END


def confirm(update, context):
    """Confirm forward settings"""
    



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
    