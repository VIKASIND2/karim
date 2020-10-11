from karim.bot.commands.signin import *
from karim.bot.commands.help import *
from karim.bot.commands.signout import *
from karim.bot.commands.forward import *
from karim.bot.commands.account import *
from karim.classes.callbacks import *


def setup(updater):
    dp = updater.dispatcher

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', client_sign_in), CommandHandler('signin', client_sign_in), CallbackQueryHandler(client_sign_in, pattern=Callbacks.LOGIN)],
        states={
            StartStates.INPUT_PHONE: [MessageHandler(Filters.text, input_phone)],
            StartStates.INPUT_PASSWORD: [MessageHandler(Filters.text, input_password)],
            StartStates.INPUT_CODE: [MessageHandler(Filters.text, input_code)]
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
            MessageStates.MESSAGE: [MessageHandler(Filters.text, select_message)],
            MessageStates.SELECT_GROUP: [CallbackQueryHandler(select_group)],
            MessageStates.CONFIRM: [CallbackQueryHandler(confirm)],
        },
        fallbacks=[CallbackQueryHandler(cancel_forward)]
    )

    # Commands
    dp.add_handler(CommandHandler("help", help_def))
    dp.add_handler(CommandHandler('account', check_account))
    dp.add_handler(signout_handler)
    dp.add_handler(start_handler)
    dp.add_handler(forwarder_handler)
    dp.add_error_handler(error)
