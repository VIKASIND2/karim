from telethon.errors.rpcerrorlist import PeerFloodError
from karim import queue, LOCALHOST
from karim.bot.texts import *
from karim.secrets import secrets
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio, time, redis, os


def create_client(user_id):
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

def send_message(user_id, target, telethon_text):
    client = create_client(user_id)
    client.connect()
    try:
        client.send_message(target, telethon_text)
        time.wait(35)
        result= True
    except PeerFloodError as error:
        print('PeerFloodLimit reached. Account may be restricted or blocked: ', error)
        result= error
    except Exception as error:
        print('Error in sending message ', error)
        result= error
    client.disconnect()
    return result

def queue_messages(targets, context, forwarder, client=None):
    if not client:
        client = create_client(forwarder.user_id)
    failed = []
    success = 0
    client.disconnect()
    for target in targets:
        result = queue.enqueue(send_message, forwarder.user_id, target, forwarder.telethon_text)
        if result:
            # Message Sent successfully
            context.bot.send_message(forwarder.user_id, sending_messages_text.format(success))
            success += 1
        elif result is PeerFloodError:
            # Flood
            failed.append(target)
            context.bot.report_error(result)
        else:
            # Error
            failed.append(target)
            context.bot.report_error(result)
        
    client.disconnect()
    return success