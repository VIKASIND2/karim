import os, redis, asyncio, time
from rq import Worker, Queue, Connection
from telethon.errors.rpcerrorlist import PeerFloodError
from karim import queue, LOCALHOST
from karim.bot.texts import *
from karim.secrets import secrets
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

listen = ['high', 'default', 'low']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

def create_client(self):
    """Creates and returns a TelegramClient"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    # TODO
    # proxy=(socks.SOCKS5, '127.0.0.1', 4444)

    if LOCALHOST:
        session = 'karim/bot/persistence/{}'.format(self.user_id)
    else:
        session_string = os.environ.get('session:{}'.format(self.user_id))
        if not session_string:
            try:
                # Falling Back to RedisSession
                print('LOADING REDIS SESSION')
                connector = redis.from_url(os.environ.get('REDIS_URL'))
                string = connector.get('session:{}'.format(self.user_id))
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

def send_message(self, target):
    client = self.create_client()
    client.connect()
    try:
        client.send_message(target, self.telethon_text)
        result= True
    except PeerFloodError as error:
        print('PeerFloodLimit reached. Account may be restricted or blocked: ', error)
        result= error
    except Exception as error:
        print('Error in sending message ', error)
        result= error
    client.disconnect()
    return result

def queue_messages(self, targets, context, client=None):
    if not client:
        client = self.create_client()
    failed = []
    success = 0
    client.disconnect()
    for target in targets:
        result = queue.enqueue(self.send_message, target, client)
        if result:
            # Message Sent successfully
            context.bot.send_message(self.user_id, sending_messages_text.format(success))
            success += 1
        elif result is PeerFloodError:
            # Flood
            failed.append(target)
            context.bot.report_error(result)
        else:
            # Error
            failed.append(target)
            context.bot.report_error(result)
        time.sleep(30)
    client.disconnect()
    return success