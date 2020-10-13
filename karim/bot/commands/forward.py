import telethon
from telethon.errors.rpcbaseerrors import UnauthorizedError
from telethon.errors.rpcerrorlist import PeerFloodError
from karim.bot.commands import *
import time

@run_async
@send_typing_action
def forward_message(update, context):
    """Initialize Forwarder Conversation. Ask for message input"""
    if not check_auth(update, context):
        return ConversationHandler.END
    forwarder = Forwarder(Persistence.FORWARDER, chat_id=update.effective_chat.id, user_id=update.effective_chat.id, message_id=update.message.message_id)
    result = forwarder.check_connection()
    if result:
        # User is authorised
        # Ask for message text
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = update.effective_chat.send_message(send_message_to_forward, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)            
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


@run_async
@send_typing_action
def select_message(update, context):
    """Initialize message Conversation"""
    forwarder: Forwarder = dict_to_obj(Forwarder.deserialize(Forwarder.FORWARDER, update), method=Objects.FORWARDER)
    if not forwarder:
        # Another user tried to enter the conversation
        return
    # Set Forwarder Message
    forwarder.set_text(update.message.text_markdown_v2)
    forwarder.set_telethon_message(context.bot.username, update.message.date)

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
            forwarder.set_message(message.message_id)
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

    
@run_async
def select_group(update, context):
    forwarder: Forwarder = dict_to_obj(Forwarder.deserialize(Forwarder.FORWARDER, update), method=Objects.FORWARDER)
    if not forwarder:
        # Another user tried to enter the conversation
        return

    # GET INPUT CALLBACK 
    data = update.callback_query.data
    update.callback_query.answer()
    if data == Callbacks.CANCEL:
        # CANCEL
        return cancel_forward(update, context, forwarder=forwarder)

    elif data == Callbacks.DONE:
        # TODO DONE
        markup = CreateMarkup({Callbacks.CONFIRM: 'Confirm', Callbacks.CANCEL: 'Cancel'}).create_markup()
        text = ''
        groups = forwarder.get_groups_dict()
        for group_id in forwarder.get_selection():
            text += '\n- {}'.format(groups.get(int(group_id)))
        context.bot.delete_message(forwarder.chat_id, forwarder.message_id)
        message = update.effective_chat.send_message(confirm_forwarding.format(text), reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return MessageStates.CONFIRM

    elif data == Callbacks.LEFT:
        # Rotate Shown Groups Left
        forwarder.rotate(Callbacks.LEFT)
        markup = ForwarderMarkup(forwarder).create_markup()
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return MessageStates.SELECT_GROUP

    elif data == Callbacks.RIGHT:
        # Redraw Markup
        forwarder.rotate(Callbacks.RIGHT)
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return MessageStates.SELECT_GROUP

    elif Callbacks.UNSELECT in data:
        # Update Selections
        selected_id = data.replace(Callbacks.UNSELECT, '')
        forwarder.remove_selection(selected_id)
        # Redraw Markup
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return MessageStates.SELECT_GROUP

    elif Callbacks.SELECT in data:
        # Update Selections
        selected_id = data.replace(Callbacks.SELECT, '')
        result = forwarder.add_selection(selected_id)
        # Redraw Markup
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        if result is not Exception:
            message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
            forwarder.set_message(message.message_id)
        update.callback_query.answer()
        return MessageStates.SELECT_GROUP

    else:
        # Do Nothing - Wrong Callback
        return



@run_async
@send_typing_action
def confirm(update, context):
    """Confirm forward settings"""
    forwarder: Forwarder = dict_to_obj(Persistence.deserialize(Forwarder.FORWARDER, update), method=Objects.FORWARDER)
    if not forwarder:
        # Another user tried to enter the conversation
        return

    data = update.callback_query.data
    if data == Callbacks.CANCEL:
        context.bot.edit_message_text(cancel_forward_text, parse_mode=ParseMode.HTML, chat_id=update.effective_chat.id, message_id=forwarder.message_id)
        forwarder.discard()
        return ConversationHandler.END
    else:
        # Send Messages
        context.bot.edit_message_text(sending_messages_text, parse_mode=ParseMode.HTML, chat_id=update.effective_chat.id, message_id=forwarder.message_id)
        client = forwarder.create_client()
        client.connect()
        targets = forwarder.load_targets(client)
        success = 0
        count = 0
        mtargets = []
        secs = 15
        for target in targets:
            """try:
                if target not in (context.bot.id,):
                    print('Sending message to ', target) # TODO
                    count += 1
                    context.bot.send_queued_message(text=forwarder.text, chat_id=target, parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as error:
                print('Sending message as user bot: ', error) """
            if target not in (context.bot.id,):
                if count <= 15 and targets.index(target) <= len(targets)-1:
                    mtargets.append(target)
                else:
                    try:
                        print('Attempting sending messages...')
                        forwarder.send_messages(mtargets, client, context)
                        print('First batch sent!')
                        mtargets = []
                        count = 0
                        success += 16
                        print('Sending message as User')
                        count += 1
                        update.callback_query.edit_message_text(text=sending_messages_text.format(success, secs))
                        time.sleep(secs)
                    except PeerFloodError as error:
                        print('Message queue flood reached. Waiting 60 seconds. Error: ', error)
                        context.bot.report_error(error)
                        update.callback_query.edit_message_text(text=flood_limit_reached.format(success))
                        time.sleep(120)
                    except Exception as error:
                        print('Fatal Error in forward.confirm(): ', error)
                        update.callback_query.edit_message_text(text=error_sending_messages.format(success))
                        context.bot.report_error(error)

        client.disconnect()
        context.bot.edit_message_text(forward_successful.format(success), chat_id=forwarder.chat_id, message_id=forwarder.message_id, parse_mode=ParseMode.HTML)
        forwarder.discard()
        return ConversationHandler.END


@run_async
def cancel_forward(update, context, send_message=True, forwarder=None):
    if not forwarder:
        forwarder = dict_to_obj(Persistence.deserialize(Persistence.FORWARDER, update), method=Objects.FORWARDER)
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
    