from karim import telegram, bot, update_queue, app, BOT_TOKEN
from flask import request

@app.route('/{}'.format(BOT_TOKEN), methods=['POST'])
def receive_update():
    print('ROUTES: Received update')
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    update_queue.put(update)
    return 'ok'

@app.route('/')
def index():
    return '.'