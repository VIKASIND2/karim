from instaclient.errors.common import InvalidUserError, PrivateAccountError
from karim.bot.commands import *
from karim import instaclient

def scrape_followers(update, context):
    """
    Initialize scrape_followers Conversation
    """
    if not check_auth(update, context):
        return ConversationHandler.END
    persistence = Persistence(Persistence.SCRAPE_FOLLOWERS, update.effective_chat.id, update.effective_user.id)
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    message = update.message.reply_text(input_username_text, reply_markup = markup)
    persistence.set_message(message.message_id)
    return ScrapeStates.SELECT_USER


def select_user(update, context):
    persistence = dict_to_obj(Persistence.deserialize(Persistence.SCRAPE_FOLLOWERS, update))
    if not persistence:
        return ScrapeStates.SELECT_USER
    user = update.message.text 
    try:
        result = instaclient.is_valid_user(user)
    except InvalidUserError as error:
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        update.message.reply_text(user_not_valid_text, reply_markup=markup)
        return ScrapeStates.SELECT_USER
    except PrivateAccountError as error:
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        update.message.reply_text(user_private_text, reply_markup=markup)
        return ScrapeStates.SELECT_USER
    
    # User is valid -  select followers count
    markup = CreateMarkup({})
    

