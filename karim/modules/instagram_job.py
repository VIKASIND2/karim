from telethon.client.telegramclient import TelegramClient
from telethon.sessions.string import StringSession
from karim.classes.mq_bot import MQBot
from karim.classes.callbacks import ScrapeStates
from karim.classes.scraper import Scraper
from karim.classes.forwarder import Forwarder
from karim.secrets import secrets
from karim.modules import sheet
from karim import queue, instaclient, BOT_TOKEN
from karim.bot.texts import *

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from rq.job import Retry
from rq.registry import FailedJobRegistry, StartedJobRegistry
import time

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
    
    # Check if no other job is in queue
    check_job_queue(scraper, telegram_bot)

    # Enqueues scrape 
    job_id = random_string()
    queue.enqueue(queue_scrape, job_id, target, scraper, job_id='launch_scrape:{}'.format(job_id))


def queue_scrape(job_id, target, scraper:Scraper):
    print('queue_scrape()')
    # ENQUEUE
    job = queue.enqueue(scrape_job, user=target, job_id='{}:{}'.format(target, job_id), timeout=4500)
    # CONNECT BOT
    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    bot = TelegramClient(StringSession(), api_id, api_hash).start(bot_token=BOT_TOKEN) 
    # CHECK FAILURE
    while True:
        registry:FailedJobRegistry = FailedJobRegistry(queue=queue)
        print(registry.get_job_ids())
        time.sleep(15)
        print(registry.get_job_ids())
        result = job.result
        if not result:
            # Queue not finished yet
            bot.send_message(scraper.get_user_id(), update_scrape_status_text)
            continue
        elif '{}:{}'.format(target, job_id) in registry.get_job_ids():
            print('found target in failed ids: ', target)
            # Process Failed
            bot.send_message(scraper.get_user_id(), failed_scraping_ig_text)
            print('SCRAPE JOB ERROR: \n{}'.format(job.exc_info))
            return False
        else:
            # Result is done
            # Save result in sheets
            sheet.add_scrape(scraper.get_target(), name=scraper.get_name(), scraped=result)
            # Update user
            markup = InlineKeyboardMarkup([InlineKeyboardButton(text='Google Sheet', url=sheet.get_sheet_url())])
            bot.send_message(scraper.get_user_id(), finished_scrape_text, reply_markup=markup)
            return True


def scrape_job(user:str):
    print('scrape_job()')
    instaclient.scrape_followers(user=user)

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

    # Enqueues job 
    job_id = random_string()
    queue.enqueue(queue_send_dm, job_id, targets, message, forwarder, job_id='launch_send_dm:{}'.format(job_id))


def queue_send_dm(job_id, targets, message, forwarder):
    # ENQUEUE and save last enqueued job
    job = None
    for target in targets:
        job = queue.enqueue(send_dm_job, user=target, message=message, job_id='{}:{}'.format(target, job_id), timeout=120)
    # CONNECT BOT
    api_id = secrets.get_var('API_ID')
    api_hash = secrets.get_var('API_HASH')
    bot = TelegramClient(StringSession(), api_id, api_hash).start(bot_token=BOT_TOKEN) 
    # CHECK FAILURES AND TERMINATION
    registry:FailedJobRegistry = FailedJobRegistry(queue=queue)
    failed = 0
    while True:
        result = job.result
        if not result:
            # Queue not finished yet
            bot.send_message(forwarder.chat_id, update_scrape_status_text)
            time.sleep(20)
            continue
        else:
            # Result is done
            count = 0
            failed = registry.get_job_ids():
            for target in targets:
                if '{}:{}'.format(target, job_id) in failed:
                    count += 1
            bot.send_message(forwarder.chat_id, finished_sending_dm_text.format(count))
            return True


def send_dm_job(user:str, message:str):
    instaclient.send_dm(user=user, message=message)

        
        
        

    


