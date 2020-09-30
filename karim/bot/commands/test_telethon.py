from telethon import TelegramClient
from karim.secrets import secrets
import asyncio

def telethonMessage(update, context):
    loop = asyncio.new_event_loop()
    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    client = TelegramClient('anon', api_id, api_hash, loop=loop)
    with client:
        loop.run_until_complete(send_telethon_message(client))
     

async def send_telethon_message(client):
    me = await client.get_me()
    print('TELETHON: {}', me.username)
    await client.send_message('me', 'Testing Telethon')