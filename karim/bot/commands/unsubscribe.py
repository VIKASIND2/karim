from karim.classes import persistence
from karim.bot.commands import *
from karim.modules import sheet

def unsubscribe(update, context):
    if update.effective_user.id in secrets.get_var('USERS'):
        update.message.replu_text(admin_cannot_unsubscribe)
        return ConversationHandler.END
    elif sheet.is_subscriber(update.effective_user.id):
        # User is subscribed
        persistence = Persistence(Persistence.UNSUBSCRIBE, update.effective_chat.id, update.effective_user.id, update.message.message_id)
        update.message.reply_text
        markup = CreateMarkup({Callbacks.CONFIRM, Callbacks.CANCEL}).create_markup()
        message = update.message.reply_text(confirm_unsubscription_text, reply_markup=markup)
        persistence.set_message(message.message_id)
        return UnsubscribeStates.CONFIRM
    else:
        # User is not subscribed
        update.message.reply_text(not_subscribed_yet_text)
        return ConversationHandler.END


def confirm_unsubscription(update, context):
    persistence = dict_to_obj(Persistence.deserialize(Persistence.UNSUBSCRIBE, update), method=Objects.PERSISTENCE)
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
