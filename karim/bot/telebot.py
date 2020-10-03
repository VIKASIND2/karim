from karim.bot.commands.signin import *
from karim.bot.commands.help import *
from karim.bot.commands.signout import *
from karim.bot.commands.forward_message import *


def setup(telebot):
    update_queue = Queue()
    job_queue = JobQueue()
    dp = Dispatcher(bot=telebot, update_queue=update_queue,
                    use_context=True, job_queue=job_queue)
    job_queue.set_dispatcher(dp)

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', client_sign_in), CommandHandler('signin', client_sign_in)],
        states={
            StartStates.INPUT_PHONE: [MessageHandler(Filters.text, input_phone)],
            StartStates.INPUT_PASSWORD: [MessageHandler(Filters.text, input_password)],
            StartStates.INPUT_CODE: [MessageHandler(Filters.text, input_code)]
        },
        fallbacks=[CallbackQueryHandler(cancel_start)]
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
    dp.add_handler(CommandHandler('signout', sign_out))
    dp.add_handler(start_handler)
    dp.add_handler(forwarder_handler)
    dp.add_error_handler(error)

    thread = Thread(target=dp.start, name='dispatcher')
    thread.start()

    return update_queue