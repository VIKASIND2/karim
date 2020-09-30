from karim.bot.commands.test_telethon import *
from karim.bot.commands.help import *

def setup(token, telebot):
    update_queue = Queue()
    job_queue = JobQueue()
    dp = Dispatcher(bot=telebot, update_queue=update_queue,
                    use_context=True, job_queue=job_queue)
    job_queue.set_dispatcher(dp)

    # Commands
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("telethon", telethonMessage))
    dp.add_error_handler(error)

    thread = Thread(target=dp.start, name='dispatcher')
    thread.start()

    return update_queue