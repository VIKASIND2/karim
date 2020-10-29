from karim.classes.mq_bot import MQBot
from karim.classes.callbacks import ScrapeStates
from karim.classes.scraper import Scraper
from karim.classes.forwarder import Forwarder
from karim.modules import sheet
from karim import queue, instaclient
from karim.bot.texts import *

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from rq.job import Retry
from rq.registry import FailedJobRegistry, StartedJobRegistry
import time

BOT = None


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
    global BOT
    BOT = telegram_bot
    queue.enqueue(queue_scrape, target, scraper, job_id='launch_scrape:{}'.format(target))


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
    global BOT
    BOT = telegram_bot

    queue.enqueue(queue_send_dm, targets, message, forwarder, job_id='launch_send_dm')


def queue_scrape(target, scraper:Scraper):
    job = queue.enqueue(instaclient.scrape_followers, user=target, job_id=target)   
    while True:
        result = job.result
        registry:FailedJobRegistry = FailedJobRegistry(queue=queue)
        if target in registry.get_job_ids():
            # Process Failed
            BOT.send_message(chat_id=scraper.get_user_id(), text=failed_scraping_ig_text)
            return False
        elif not result:
            # Queue not finished yet
            BOT.send_message(chat_id=scraper.get_user_id(), text=update_scrape_status_text)
            time.sleep(20)
            continue
        else:
            # Result is done
            # Save result in sheets
            sheet.add_scrape(scraper.get_target(), name=scraper.get_name(), scraped=result)
            # Update user
            markup = InlineKeyboardMarkup([InlineKeyboardButton(text='Google Sheet', url=sheet.get_sheet_url())])
            BOT.send_message(chat_id=scraper.get_user_id(), text=finished_scrape_text, reply_markup=markup)
            return True


def queue_send_dm(targets, message, forwarder):
    job = None
    for target in targets:
        job = queue.enqueue(instaclient.send_dm, user=target, message=message, timeout=120)
    registry:FailedJobRegistry = FailedJobRegistry(queue=queue)
    failed = 0
    while True:
        result = job.result
        if not result:
            # Queue not finished yet
            BOT.send_message(chat_id=forwarder.chat_id, text=update_scrape_status_text)
            time.sleep(20)
            continue
        else:
            # Result is done
            for job in registry.get_job_ids():
                if job in targets:
                    failed += 1
            BOT.send_message(chat_id=forwarder.chat_id, text=finished_sending_dm_text.format(failed))
            return True

        
        
        

    


