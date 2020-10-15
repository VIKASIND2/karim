from rq.job import Retry
from telethon.errors.rpcerrorlist import PeerFloodError
from karim import queue, LOCALHOST
from karim.bot.texts import *
from karim.secrets import secrets
from karim.classes.mq_bot import MQBot
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio, time, redis, os


def create_client(user_id, bot=False):
    """Creates and returns a TelegramClient"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    # TODO
    # proxy=(socks.SOCKS5, '127.0.0.1', 4444)
    if LOCALHOST:
        session = 'karim/bot/persistence/{}'.format(user_id)
    else:
        session_string = os.environ.get('session:{}'.format(user_id))
        if not session_string:
            try:
                # Falling Back to RedisSession
                print('LOADING REDIS SESSION')
                connector = redis.from_url(os.environ.get('REDIS_URL'))
                string = connector.get('session:{}'.format(user_id))
                print('SESSION STRING OUTPUTTED')
                if string:
                    # Session is stored in Redis
                    decoded_string = string.decode("utf-8") 
                    session = StringSession(decoded_string)
                else:
                    session = StringSession()
                connector.close()
            except Exception as error:
                # No Session Error
                print('Error in session_manager.create_client(): ', error)
                raise error
        else:
            try:
                session = StringSession(session_string)
            except Exception as error:
                print('Error in session_manager.create_client(): ', error)
                raise error
    try:
        client = TelegramClient(session, api_id, api_hash, loop=loop) #proxy = proxy
    except Exception as error:
        print('Error in session_manager.create_client(): ', error)
        raise error
    print('TELEGRAM CLIENT WITH SESSION CREATED')
    return client


def send_message(user_id, bot_id, target, index, targets_len, telethon_text):
    # Send Message:
    client = create_client(user_id)
    client.connect()
    try:
        entity = client.get_input_entity(target)
        client.send_message(entity, telethon_text)
        print('Message {} sent successfully'.format(index+1))
    except PeerFloodError as error:
        print('PeerFloodLimit reached. Account may be restricted or blocked: ', error)
    except Exception as error:
        print('Error in sending message to user: ', error)

    entity = client.get_input_entity(os.environ.get('BOT_USERNAME'))
    messages = client.get_messages(entity, limit=1, from_user=bot_id)
    try:
        message = messages[0]
    except:
        message = None
        for message in messages:
            message = message
    client.disconnect()

    # Edit Bot Message
    try:
        bot_client = create_client('bot', bot=True).start(bot_token=os.environ.get('BOT_TOKEN'))
        if index == targets_len-1:
            print('Editing final message')
            entity = bot_client.get_input_entity(user_id)
            try:
                bot_client.edit_message(message, text=message_queue_finished)
            except Exception as error:
                print('Error in editing message: ', error)
                bot_client.send_message(entity, message=message_queue_finished)
        else:
            entity = bot_client.get_input_entity(user_id)
            print('Editing in process message')
            bot_client.edit_message(message, text=sending_messages_text.format(len(targets_len), index+1))
        bot_client.disconnect()
    except Exception as error:
        print('Error in editing update message: ', error)
    time.sleep(45)


def queue_messages(targets, context, forwarder, client=None):
    for index, target in enumerate(targets):
        queue.enqueue(send_message, user_id=forwarder.user_id, bot_id=context.bot.id, target=target, index=index, targets_len=len(targets), telethon_text=forwarder.telethon_text, retry=Retry(max=2, interval=[35, 45]))       
