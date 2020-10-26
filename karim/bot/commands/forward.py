from telegram.ext import updater
import telethon
from telethon.errors.rpcbaseerrors import UnauthorizedError
from telethon.errors.rpcerrorlist import PeerFloodError
from karim.bot.commands import *
from karim.modules import message_job, instagram_job
from karim.modules import sheet
from karim import queue
import time

@run_async
@send_typing_action
def forward_message(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END
    forwarder = Forwarder(Persistence.FORWARDER, chat_id=update.effective_chat.id, user_id=update.effective_chat.id, message_id=update.message.message_id)
    result = forwarder.check_connection()
    if result:
        # User is authorised, ask mode input
        markup = CreateMarkup({Callbacks.NEWSLETTER: 'Newsletter', Callbacks.INSTAGRAM_DM: 'Instagram DMs', Callbacks.TELEGRAM: 'Telegram Groups', Callbacks.CANCEL: 'Cancel'})
        message = update.effective_chat.send_message(select_forward_mode_text, reply_markup=markup)
        forwarder.set_message(message.message_id)
        return ForwarderStates.MODE
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
def forward_mode(update, context):
    forwarder: Forwarder = Forwarder.deserialize(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return
    mode = update.callback_query.data
    if mode == Callbacks.CANCEL:
        return cancel_forward(update, context, forwarder=forwarder)
    forwarder.set_mode(mode)
    # Ask for message text
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    message = update.effective_chat.send_message(send_message_to_forward, reply_markup=markup, parse_mode=ParseMode.HTML)
    forwarder.set_message(message.message_id)            
    return ForwarderStates.MESSAGE


@run_async
@send_typing_action
def select_message(update, context):
    forwarder: Forwarder = Forwarder.deserialize(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return
    # Set Forwarder Message
    forwarder.set_text(update.message.text_markdown_v2)
    forwarder.set_telethon_message(context.bot.username, update.message.date)

    # MODE
    if forwarder.get_mode() == Callbacks.NEWSLETTER:
        users = sheet.get_subscribers()
        markup = CreateMarkup({Callbacks.CONFIRM: 'Confirm', Callbacks.CANCEL: 'Cancel'}).create_markup()
        update.message.reply_text(text=confirm_send_newsletter_text.format(len(users)), reply_markup=markup)
        return ForwarderStates.CONFIRM

    elif forwarder.get_mode() == Callbacks.INSTAGRAM_DM:
        # TODO SELECT SCRAPED SELECTION
        # Get Scraped from Sheet
        scraped = sheet.get_scraped()
        if not scraped:
            # No selection available, ask to start  a new scrape
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=forwarder.message_id, text=no_selection_available_text)
            return ConversationHandler.END
        else:
            markup_dict = {}
            for item in scraped:
                markup_dict[scraped[0]] = scraped[1]
            markup_dict[Callbacks.CANCEL] = 'Cancel'
            markup = CreateMarkup(markup_dict).create_markup()
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=forwarder.message_id, reply_markup=markup)
            return ForwarderStates.SELECT_SCRAPE

    elif forwarder.get_mode() == Callbacks.TELEGRAM:
        # SEND TO TELEGRAM GROUP SELECTION
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
                return ForwarderStates.SELECT_GROUP
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
@send_typing_action
def select_scrape(update, context):
    forwarder: Forwarder = Forwarder.deserialize(Forwarder.FORWARDER, update)
    if not forwarder:
        # Another user tried to enter the conversation
        return

    # GET INPUT CALLBACK 
    data = update.callback_query.data
    update.callback_query.answer()
    if data == Callbacks.CANCEL:
        return cancel_forward(update, context, forwarder)
    else:
        scrape = sheet.get_scraped(username=data)
        targets_str = scrape[2]
        targets = list(targets_str)
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        context.bot.edit_message_text(chat_id=update.effective_chat.id, 
        message_id=forwarder.message_id, text=confirm_send_dm_text.format(len(targets)), reply_markup=markup)
        forwarder.set_users(targets)
        return ForwarderStates.CONFIRM
        #instagram_job.queue_send_dm(targets, forwarder.text)
    

@run_async
def select_group(update, context):
    forwarder: Forwarder = Forwarder.deserialize(Forwarder.FORWARDER, update)
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
        if len(forwarder.get_selection()) == 0:
            forwarder.set_message(forwarder.message_id)
            return ForwarderStates.SELECT_GROUP

        markup = CreateMarkup({Callbacks.CONFIRM: 'Confirm', Callbacks.CANCEL: 'Cancel'}).create_markup()
        text = ''
        groups = forwarder.get_groups_dict()
        for group_id in forwarder.get_selection():
            text += '\n- {}'.format(groups.get(int(group_id)))
        context.bot.delete_message(forwarder.chat_id, forwarder.message_id)
        message = update.effective_chat.send_message(confirm_forwarding.format(text), reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return ForwarderStates.CONFIRM

    elif data == Callbacks.LEFT:
        # Rotate Shown Groups Left
        forwarder.rotate(Callbacks.LEFT)
        markup = ForwarderMarkup(forwarder).create_markup()
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return ForwarderStates.SELECT_GROUP

    elif data == Callbacks.RIGHT:
        # Redraw Markup
        forwarder.rotate(Callbacks.RIGHT)
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return ForwarderStates.SELECT_GROUP

    elif Callbacks.UNSELECT in data:
        # Update Selections
        selected_id = data.replace(Callbacks.UNSELECT, '')
        forwarder.remove_selection(selected_id)
        # Redraw Markup
        markup = ForwarderMarkup(forwarder).create_markup()
        # Send Message
        message = update.callback_query.edit_message_text(select_group_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        forwarder.set_message(message.message_id)
        return ForwarderStates.SELECT_GROUP

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
        return ForwarderStates.SELECT_GROUP

    else:
        # Do Nothing - Wrong Callback
        return


@run_async
@send_typing_action
def confirm(update, context):
    """Confirm forward settings"""
    forwarder: Forwarder = Persistence.deserialize(Forwarder.FORWARDER, update)
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
        if forwarder.get_mode() == Callbacks.TELEGRAM:
            context.bot.edit_message_text(preparing_queue_text, parse_mode=ParseMode.HTML, chat_id=update.effective_chat.id, message_id=forwarder.message_id)
            targets = forwarder.load_targets()
            message_job.queue_messages(targets, context, forwarder)
            forwarder.discard()
            return ConversationHandler.END

        elif forwarder.get_mode() == Callbacks.NEWSLETTER:
            targets = sheet.get_subscribers()
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=forwarder.message_id, text=inform_sending_newsletter_text)
            message_job.queue_messages(targets, context, forwarder)
            return ConversationHandler.END

        elif forwarder.get_mode() == Callbacks.INSTAGRAM_DM:
            users = forwarder.get_users()
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=forwarder.message_id, text=inform_sending_dms_text)
            instagram_job.queue_send_dm(users, forwarder.text)
            return ConversationHandler.END


@run_async
def cancel_forward(update, context, send_message=True, forwarder=None):
    if not forwarder:
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
    