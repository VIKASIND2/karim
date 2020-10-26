from karim.classes import persistence
from karim.bot.commands import *
from karim.modules import sheet

def unsubscribe_command(update, context):
    if update.effective_user.id in list(secrets.get_var('USERS')):
        update.message.replu_text(admin_cannot_unsubscribe)
        return ConversationHandler.END
    message = update.effective_chat.send_message(text=checking_subscription)
    subscribed = sheet.is_subscriber(update.effective_user.id)
    if subscribed:
        print('Subscribed')
        # User is subscribed
        persistence = Persistence(Persistence.UNSUBSCRIBE, update.effective_chat.id, update.effective_user.id, update.message.message_id)
        update.message.reply_text
        markup = CreateMarkup({Callbacks.CONFIRM: 'Confirm', Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=confirm_unsubscription_text, reply_markup=markup)
        persistence.set_message(message.message_id)
        return UnsubscribeStates.CONFIRM
    else:
        print('Not subscribed')
        # User is not subscribed
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=not_subscribed_yet_text)
        return ConversationHandler.END


def confirm_unsubscription(update, context):
    persistence = Persistence.deserialize(Persistence.UNSUBSCRIBE, update)
    if not persistence:
        # Another user tried to enter the conversation
        update.callback_query.answer()
        return UnsubscribeStates.CONFIRM
    else:
        # Unsubscribe user
        query = update.callback_query
        if query.data == Callbacks.CONFIRM:
            # Confirm unsubscription
            sheet.remove_subscriber(update.effective_user.id)
            query.answer()
            context.bot.edit_message_text(unsubscription_successful_text, chat_id=update.effective_chat.id, message_id=persistence.message_id)
            return ConversationHandler.END
        else:
            query.answer()
            context.bot.edit_message_text(unsubscription_cancelled_text, chat_id=update.effective_chat.id, message_id=persistence.message_id)
            return ConversationHandler.END
