from karim.classes.scraper import Scraper
from instaclient.errors.common import InvalidUserError, PrivateAccountError
from karim.bot.commands import *
from karim.modules import instagram_job
from karim import instaclient


@run_async
@send_typing_action
def scrape_followers(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END
    scraper = Scraper(Persistence.SCRAPE_FOLLOWERS, update.effective_chat.id, update.effective_user.id)
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    message = update.message.reply_text(input_username_text, reply_markup = markup)
    scraper.set_message(message.message_id)
    return ScrapeStates.SELECT_TARGET


@run_async
@send_typing_action
def select_target(update, context):
    scraper:Scraper = Scraper.deserialize(Persistence.SCRAPE_FOLLOWERS, update)
    if not scraper:
        return ScrapeStates.SELECT_TARGET
    user = update.message.text
    try:
        
        result = instaclient.is_valid_user(user)
        scraper.set_target(user)
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = update.message.reply_text(select_name_text, reply_markup=markup)
        return ScrapeStates.SELECT_NAME

    except InvalidUserError as error:
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = update.message.reply_text(user_not_valid_text.format(user), reply_markup=markup)
        scraper.set_message(message.message_id)
        return ScrapeStates.SELECT_TARGET

    except PrivateAccountError as error:
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = update.message.reply_text(user_private_text, reply_markup=markup)
        scraper.set_message(message.message_id)
        return ScrapeStates.SELECT_TARGET
    
    except:
        return cancel_scrape(update, context, scraper)


@run_async
@send_typing_action
def select_name(update, context):
    scraper:Scraper = Scraper.deserialize(Persistence.SCRAPE_FOLLOWERS, update)
    if not scraper:
        return ScrapeStates.SELECT_NAME
    name = update.message.text
    scraper.set_name(name)
    # User is valid -  select followers count
    markup = CreateMarkup({Callbacks.TEN: '10', Callbacks.HUNDRED: '100', Callbacks.FIVEHUNDRED: '500', Callbacks.THOUSAND: '1000', Callbacks.CANCEL: 'Cancel'}).create_markup()
    message = update.message.reply_text(select_count_text, reply_markup=markup)
    scraper.set_message(message.message_id)


@run_async
@send_typing_action
def select_count(update, context):
    scraper:Scraper = Scraper.deserialize(Persistence.SCRAPE_FOLLOWERS, update)
    if not scraper:
        return ScrapeStates.SELECT_COUNT

    data = update.callback_query.data
    print('SCRAPE DATA: ', data)
    if data == Callbacks.TEN:
        scraper.set_count(10)
    elif data == Callbacks.HUNDRED:
        scraper.set_count(100)
    elif data == Callbacks.FIVEHUNDRED:
        scraper.set_count(500)
    elif data == Callbacks.THOUSAND:
        scraper.set_count(1000)
    else:
        #cancel
        print('Cancel Scrape')
        return cancel_scrape(update, context, scraper)

    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=scraper.message_id, text=update_scraping_ig_text.format(scraper.get_count()))
    instagram_job.queue_scrape(scraper.get_target(), scraper.get_count(), context, scraper)
    return ConversationHandler.END


@run_async
@send_typing_action
def cancel_scrape(update, context, scraper:Scraper=None):
    if not scraper:
        scraper:Scraper = Scraper.deserialize(Persistence.SCRAPE_FOLLOWERS, update)
        if not scraper:
            return
    try:
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=scraper.message_id, text=cancelling_scrape_text)
    except:
        update.effective_chat.send_message(text=cancelling_scrape_text)
    scraper.discard()
    return ConversationHandler.END



    

