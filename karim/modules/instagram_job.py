from telethon.client import buttons
from telethon.client.telegramclient import TelegramClient
from telethon.sessions.string import StringSession
from karim.classes.mq_bot import MQBot
from karim.classes.callbacks import ScrapeStates
from karim.classes.scraper import Scraper
from karim.classes.forwarder import Forwarder
from karim.classes.insta_session import InstaSession
from karim.secrets import secrets
from karim.modules import sheet
from karim import queue, instaclient, BOT_TOKEN
from karim.bot.texts import *
from telethon.tl.types import KeyboardButtonUrl

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram import ParseMode
from rq.job import Job, Retry
from rq.registry import FailedJobRegistry, StartedJobRegistry, FinishedJobRegistry
import time, random, string, redis, os

SCRAPE = 'scrape'
CHECKSCRAPE = 'checkscrape'
DM = 'dm'
CHECKDM = 'checkdm'

def random_string():
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(6)))
    return result_str


def check_job_queue(obj: Scraper or Forwarder, telegram_bot:MQBot):
    """
    Checks if any launch_scrape or launch_send_dm jobs are in the RQ Queue. If that's the case, sends a message to the user informing that another job is in the queue and that the newly requested job will be executed later.

    Args:
        obj (ScraperorForwarder): The object to get the `chat_id` from
        telegram_bot (MQbot): Bot to use to send messages
    """
    # Check if no other job is in queue
    registry = StartedJobRegistry(queue=queue)
    for job_id in registry.get_job_ids():
        if 'launch_scrape' in job_id:
            text = scrape_job_in_queue_text
            telegram_bot.send_message(chat_id=obj.chat_id, text=text)
        elif 'launch_send_dm' in job_id:
            text = dm_job_in_queue_text
            telegram_bot.send_message(chat_id=obj.chat_id, text=text)


def process_update_callback(obj: Scraper or Forwarder, message:str, message_id:int=None):
    """
    process_update_callback sends an update message to the user, to inform of the status of the current process. This method can be used as a callback in another method.

    Args:
        obj (ScraperorForwarder): Object to get the `chat_id` and `message_id` from.
        message (str): The text to send via message
        message_id (int, optional): If this argument is defined, then the method will try to edit the message matching the `message_id` of the `obj`. Defaults to None.
    """
    from karim import telegram_bot as bot
    if message_id:
        try:
            bot.edit_message_text(text=message, chat_id=obj.chat_id, message_id=obj.get_message_id(), parse_mode=ParseMode.HTML)
            return
        except: pass
    bot.send_message(obj.chat_id, text=message, parse_mode=ParseMode.HTML)
    return


# SCRAPE JOB HANDLER ----------------------------------------------------------------------------
def launch_scrape(target:str, scraper:Scraper, telegram_bot:MQBot):
    """
    Add scrape job to the Worker queue. 
    
    This method abstracts the process of enqueing scrape jobs. It enqueues a method which takes care of enqueing the scrape jobs and returning a response. This makes it possible to add the `queue_scrape()` method to the Worker queue, hence it allows for it to run in the background.

    Args:
        target (str): Username of the instagram user to scrape from
        scraper (Scraper): Scraper object used to initialize the scrape
        telegram_bot (MQbot): Bot to use to send messages
    """
    
    # Check if other jobs are in queue
    check_job_queue(scraper, telegram_bot)

    # COMPILE SCRAPE
    # Add scrape job
    identifier = random_string()
    scrape_id = '{}:{}:{}'.format(SCRAPE, target, identifier)
    job = queue.enqueue(scrape_job, target, scraper, job_id=scrape_id, job_timeout=4500)
    # Add checker job
    checker_id = '{}:{}:{}'.format(CHECKSCRAPE, target, identifier)
    checker = queue.enqueue(check_scrape_job, scrape_id, scraper, job_id=checker_id, job_timeout=300)

 
def scrape_job(user:str, scraper:Scraper):
    print('scrape_job()')
    from karim import telegram_bot
    instaclient.driver.save_screenshot('before_scrape.png')
    telegram_bot.send_photo(scraper.chat_id, photo=open('{}.png'.format('before_scrape'), 'rb'))
    try:
        instasession = InstaSession(scraper.chat_id, scraper.user_id, scraper.message_id)
        if instasession.get_creds():
            process_update_callback(scraper, logging_in_with_credentials_text, scraper.get_message_id())
            instaclient.login(instasession.username, instasession.password, check_user=False)
            time.sleep(1)
            process_update_callback(scraper, initiating_scrape_text.format(user, user))
            followers = instaclient.scrape_followers(user=user)
            return followers
        else:
            return None
    except Exception as error:
        raise error


def check_scrape_job(scrape_id:str, scraper:Scraper):
    failed = FailedJobRegistry(queue=queue)

    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    bot = TelegramClient(StringSession(), api_id, api_hash).start(bot_token=BOT_TOKEN) 

    if scrape_id in failed.get_job_ids():
        # job failed
        bot.send_message(scraper.get_user_id(), failed_scraping_ig_text)
        return False
    else:
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        conn = redis.from_url(redis_url)
        job = Job.fetch(scrape_id, connection=conn)
        result = job.result

        # Save result in sheets
        sheet.add_scrape(scraper.get_target(), name=scraper.get_name(), scraped=result)
        # Update user
        button = KeyboardButtonUrl('Google Sheet', url=sheet.get_sheet_url())
        bot.send_message(scraper.get_user_id(), finished_scrape_text, buttons=button)
        return True


# SEND DM JOB HANDLER -------------------------------------------------------------------------
def launch_send_dm(targets:list, message:str, forwarder:Forwarder, telegram_bot:MQBot):
    """
    launch_send_dm Adds send DMs jobs to the Worker queue.

    This method abstracts the process of enqueing send_dm jobs. It enqueues a method which takes care of enqueing the send_dm jobs and returning a response. This makes it possible to add the `queue_send_dm()` method to the Worker queue, hence it allows for it to run in the background.

    Args:
        targets (list): List of instagram usernames
        message (str): Message to send to the users
        forwarder (Forwarder): Forwarder object used to initialize the operation
        telegram_bot (MQbot): Bot to use to send messages
    """
    
    # Check if no other job is in queue
    check_job_queue(forwarder, telegram_bot)

    # Enqueues jobs
    identifier = random_string()
    for target in targets:
        queue.enqueue(send_dm_job, identifier, targets, message, forwarder, job_id='{}:{}:{}'.format(DM, target, identifier), job_timeout =84000)
    # Enqueue check job
    queue.enqueue(check_dm_job, identifier, forwarder, job_id='{}:{}'.format(CHECKDM, identifier))


def send_dm_job(user:str, message:str, forwarder:Forwarder):
    instaclient.send_dm(user=user, message=message)
    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    bot = TelegramClient(StringSession(), api_id, api_hash).start(bot_token=BOT_TOKEN) 
    bot.send_message(forwarder.chat_id, message_sent_to_users.format(forwarder.get_completed_dm()))
    bot.disconnect()
    forwarder.set_completed_dm()
    time.sleep(random.randrange(25, 60))
    return True


def check_dm_job(identifier:str, forwarder:Forwarder):
    failed = FailedJobRegistry(queue=queue)

    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    bot = TelegramClient(StringSession(), api_id, api_hash).start(bot_token=BOT_TOKEN) 

    count = 0
    for id in failed.get_job_ids:
        if identifier in id and DM in id:
            count += 1

    bot.send_message(forwarder.get_user_id(), finished_sending_dm_text.format(count))
    bot.disconnect()
    return True
        

    


