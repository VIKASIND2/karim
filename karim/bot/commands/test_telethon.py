import asyncio
from telethon import TelegramClient
from karim.secrets import secrets

async def telethonMessage(update, context):
    client = signIn()
    with client:
        client.loop.run_until_complete(send_telethon_message(client))
     

async def send_telethon_message(client):
    me = await client.get_me()
    print('TELETHON: {}', me.username)
    await client.send_message('me', 'Testing Telethon')

def signIn():
    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    client = TelegramClient('anon', api_id, api_hash)
    return client