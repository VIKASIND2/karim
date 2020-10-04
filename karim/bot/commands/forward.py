# TODO: Select Groups
# TODO: Select Message
# TODO: Retrieve Group Members
# TODO: Send Message
from threading import main_thread
from jinja2.runtime import markup_join
from telethon.errors.rpcbaseerrors import UnauthorizedError
from karim.bot.commands import *


@send_typing_action
def forward_message(update, context):
    """Initialize Forwarder Conversation. Ask for message input"""
    forwarder = Forwarder(update)
    result = forwarder.check_connection()
    if result:
        # User is authorised
        # Ask for message text
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = update.effective_chat.send_message(send_message_to_forward, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message)            
        return MessageStates.MESSAGE
    elif not result:
        # User is not logged in
        update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
        cancel_forward(update, context, send_message=False)
        return ConversationHandler.END
    else:
        # Error
        update.effective_chat.send_message(error_checking_connection, parse_mode=ParseMode.HTML)
        forwarder.discard()
        return ConversationHandler.END



@send_typing_action
def select_message(update, context):
    """Initialize message Conversation"""
    forwarder: Forwarder = Forwarder.deserialize(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return
    # Set Forwarder Message
    forwarder.set_text(update.message)

    # SEND GROUP SELECTION
    # Check User Connection to the Client
    result = forwarder.check_connection()
    if result:
        # User is authorised
        # Get Group List
        try:
            # Scrape Groups
            groups = forwarder.scrape_dialogues()
            # Create Markup
            markup = ForwarderMarkup(forwarder)
            reply_markup = markup.create_markup()
            # Send Message
            message = update.effective_chat.send_message(select_group_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            forwarder.set_message(message)
            return MessageStates.SELECT_GROUP
        except UnauthorizedError:
            # User is not logged in
            update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
            cancel_forward(update, context, send_message=False)
            return ConversationHandler.END
        except:
            update.message.reply_text(failed_scrape_dialogues, parse_mode=ParseMode.HTML)
            cancel_forward(update, context, send_message=False)
            return ConversationHandler.END
    elif not result:
        # User is not logged in
        update.message.reply_text(client_not_connected, parse_mode=ParseMode.HTML)
        cancel_forward(update, context, send_message=False)
        return ConversationHandler.END
    else:
        # Error
        update.effective_chat.send_message(error_checking_connection, parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    
def select_group(update, context):
    forwarder: Forwarder = Forwarder.deserialize(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return

    # GET INPUT CALLBACK 
    data = update.callback_query.data
    update.callback_query.answer()
    print(data)
    if data == Callbacks.CANCEL:
        # CANCEL
        return cancel_forward(update, context)

    elif data == Callbacks.DONE:
        # TODO DONE
        print('Done')
        markup = CreateMarkup({Callbacks.CONFIRM: 'Confirm', Callbacks.CANCEL: 'Cancel'}).create_markup()
        text = ''
        for group in list(forwarder.selected.values()):
            text += '\n- {}'.format(group)
        forwarder.message.delete()
        message = forwarder.text.reply_text(confirm_forwarding.format(text), reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message)
        return MessageStates.CONFIRM

    elif data == Callbacks.LEFT:
        # Rotate Shown Groups Left
        forwarder.rotate(Callbacks.LEFT)
        markup = ForwarderMarkup(forwarder).create_markup()
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message)
        return MessageStates.SELECT_GROUP

    elif data == Callbacks.RIGHT:
        # Redraw Markup
        forwarder.rotate(Callbacks.RIGHT)
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message)
        return MessageStates.SELECT_GROUP

    elif Callbacks.UNSELECT in data:
        # Update Selections
        selected_id = data.replace(Callbacks.UNSELECT, '')
        forwarder.remove_selection(selected_id)
        # Redraw Markup
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message)
        return MessageStates.SELECT_GROUP

    elif Callbacks.SELECT in data:
        # Update Selections
        selected_id = data.replace(Callbacks.SELECT, '')
        forwarder.add_selection(selected_id)
        # Redraw Markup
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message)
        return MessageStates.SELECT_GROUP

    else:
        # Do Nothing - Wrong Callback
        return


    


@send_typing_action
def confirm(update, context):
    """Confirm forward settings"""
    forwarder: Forwarder = Persistence.deserialize(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return

    data = update.callback_query.data
    if data is Callbacks.CANCEL:
        forwarder.message.edit_text(cancel_forward_text, parse_mode=ParseMode.HTML)
        forwarder.discard()
        return ConversationHandler.END
    else:
        # Send Messages
        count = forwarder.send()
        forwarder.message.edit_text(forward_successful.format(count[0], count[1]), parse_mode=ParseMode.HTML)
        forwarder.discard()
        return ConversationHandler.END


def cancel_forward(update, context, send_message=True):
    forwarder = Persistence.deserialize(Persistence.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return
    if send_message:
        if update.callback_query is not None:
            update.callback_query.edit_message_text('Message Forward Cancelled')
        else:
            update.effective_chat.send_message('Message Forward Cancelled')
    forwarder.discard()
    return ConversationHandler.END
    