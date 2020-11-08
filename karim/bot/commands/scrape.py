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
    # Check IG Connection
    message = update.effective_chat.send_message(text=checking_ig_status)
    result = instaclient.check_status()
    if result:
        scraper = Scraper(Persistence.SCRAPE_FOLLOWERS, update.effective_chat.id, update.effective_user.id)
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        context.bot.edit_message_text(text=input_username_text, message_id=message.message_id, chat_id=update.effective_chat.id, reply_markup=markup)
        scraper.set_message(message.message_id)
        return ScrapeStates.SELECT_TARGET
    else:
        context.bot.edit_message_text(text=ig_not_logged_in_text, message_id=message.message_id, chat_id=update.effective_chat.id)
        return ConversationHandler.END


@run_async
@send_typing_action
def select_target(update, context):
    scraper:Scraper = Scraper.deserialize(Persistence.SCRAPE_FOLLOWERS, update)
    if not scraper:
        return ScrapeStates.SELECT_TARGET
    user = update.message.text
    try:
        message = update.effective_chat.send_message(text=checking_user_text)
        scraper.set_message(message.message_id)
        result = instaclient.is_valid_user(user)
        scraper.set_target(user)
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = message.edit_text(select_name_text, reply_markup=markup)
        return ScrapeStates.SELECT_NAME

    except InvalidUserError as error:
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = context.bot.edit_message_text(text=user_not_valid_text.format(user), reply_markup=markup, chat_id=scraper.chat_id, message_id=scraper.message_id)
        scraper.set_message(message.message_id)
        return ScrapeStates.SELECT_TARGET

    except PrivateAccountError as error:
        markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
        message = context.bot.edit_message_text(text=user_private_text, reply_markup=markup, chat_id=scraper.chat_id, message_id=scraper.message_id)
        scraper.set_message(message.message_id)
        return ScrapeStates.SELECT_TARGET
    
    except Exception as error:
        context.bot.report_error(error)
        return cancel_scrape(update, context, scraper)


@run_async
@send_typing_action
def select_name(update, context):
    scraper:Scraper = Scraper.deserialize(Persistence.SCRAPE_FOLLOWERS, update)
    if not scraper:
        return ScrapeStates.SELECT_NAME
    name = update.message.text
    scraper.set_name(name)
    # User is valid -  confirm
    markup = CreateMarkup({Callbacks.CONFIRM: 'Confirm', Callbacks.CANCEL: 'Cancel'}).create_markup()
    message = update.message.reply_text(confirm_scrape_text.format(scraper.target), reply_markup=markup)
    scraper.set_message(message.message_id)
    return ScrapeStates.CONFIRM


@run_async
@send_typing_action
def confirm_scrape(update, context):
    scraper:Scraper = Scraper.deserialize(Persistence.SCRAPE_FOLLOWERS, update)
    if not scraper:
        return ScrapeStates.CONFIRM

    data = update.callback_query.data
    if data == Callbacks.CONFIRM:
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=scraper.message_id, text=update_scraping_ig_text)
        instagram_job.launch_scrape(scraper.get_target(), scraper=scraper, telegram_bot=context.bot)
        scraper.discard()
        return ConversationHandler.END
    elif data == Callbacks.CANCEL:
        print('Cancel Scrape')
        return cancel_scrape(update, context, scraper)


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



    

