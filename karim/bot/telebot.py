from logging import Filter
from karim.bot.commands.signin import *
from karim.bot.commands.help import *
from karim.bot.commands.signout import *
from karim.bot.commands.scrape_followers import *
from karim.bot.commands.forward import *
from karim.bot.commands.account import *
from karim.bot.commands.unsubscribe import *
from karim.bot.commands.start import *
from karim.classes.callbacks import *


def setup(updater):
    dp = updater.dispatcher

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('signin', client_sign_in), CallbackQueryHandler(client_sign_in, pattern=Callbacks.LOGIN)],
        states={
            LogInStates.INPUT_PHONE: [MessageHandler(Filters.text, input_phone)],
            LogInStates.INPUT_PASSWORD: [MessageHandler(Filters.text, input_password)],
            LogInStates.INPUT_CODE: [MessageHandler(Filters.text, input_code), CallbackQueryHandler(input_code, pattern=Callbacks.REQUEST_CODE)]
        },
        fallbacks=[CallbackQueryHandler(cancel_start)]
    )
    signout_handler = ConversationHandler(
        entry_points=[CommandHandler('signout', sign_out), CallbackQueryHandler(sign_out, pattern=Callbacks.LOGOUT)],
        states={
            LogOutStates.CONFIRM: [CallbackQueryHandler(confirm_sign_out, pattern=Callbacks.LOGOUT)]
        },
        fallbacks=[CallbackQueryHandler(cancel_sign_out)]
    )
    forwarder_handler = ConversationHandler(
        entry_points=[CommandHandler('forward', forward_message)],
        states = {
            ForwarderStates.MODE: [],
            ForwarderStates.MESSAGE: [MessageHandler(Filters.text, select_message)],
            ForwarderStates.SELECT_SCRAPE: [CallbackQueryHandler(select_scrape)],
            ForwarderStates.SELECT_GROUP: [CallbackQueryHandler(select_group)],
            ForwarderStates.CONFIRM: [CallbackQueryHandler(confirm)],
        },
        fallbacks=[CallbackQueryHandler(cancel_forward)]
    )
    scrape_handler = ConversationHandler(
        entry_points=[CommandHandler('scrape', scrape_followers)],
        states={
            ScrapeStates.SELECT_TARGET: [MessageHandler(Filters.text, select_target)],
            ScrapeStates.SELECT_NAME: [MessageHandler(Filters.text, select_name)],
            ScrapeStates.SELECT_COUNT: [CallbackQueryHandler(select_count)],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_scrape)
        ]
    )
    unsubscribe_handler = ConversationHandler(
        entry_points=[CommandHandler('unsubscribe', unsubscribe)],
        states={
            UnsubscribeStates.CONFIRM: [CallbackQueryHandler(confirm_unsubscription)]
        },
        fallbacks=[]
    )

    # Commands
    dp.add_handler(CommandHandler("help", help_def))
    dp.add_handler(CommandHandler('account', check_account))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(scrape_handler)
    dp.add_handler(signout_handler)
    dp.add_handler(start_handler)
    dp.add_handler(forwarder_handler)
    dp.add_handler(unsubscribe_handler)
    dp.add_error_handler(error)
