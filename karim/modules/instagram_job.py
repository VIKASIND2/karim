from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from karim.classes.scraper import Scraper
from karim.modules import sheet
from rq.job import Retry
from rq.registry import FailedJobRegistry
from karim import queue, instaclient
from karim.bot.texts import *
import time

def queue_scrape(target, count, context, scraper:Scraper):
    job = queue.enqueue(instaclient.scrape_followers, user=target, count=count, callback_frequency=count//10, timeout=84000, job_id=target)   
    while True:
        result = job.result
        registry:FailedJobRegistry = FailedJobRegistry(queue=queue)
        if target in registry.get_job_ids():
            # Process Failed
            context.bot.send_message(chat_id=scraper.get_user_id(), text=failed_scraping_ig_text)
            return False
        elif not result:
            # Queue not finished yet
            context.bot.send_message(chat_id=scraper.get_user_id(), text=update_scrape_status_text)
            time.sleep(20)
            continue
        else:
            # Result is done
            # Save result in sheets
            sheet.add_scrape(scraper.get_target(), name=scraper.get_name(), scraped=result)
            # Update user
            markup = InlineKeyboardMarkup([InlineKeyboardButton(text='Google Sheet', url=sheet.get_sheet_url())])
            context.bot.send_message(chat_id=scraper.get_user_id(), text=finished_scrape_text.format(count))
            return True

def queue_send_dm(targets, message, context, forwarder):
    job = None
    for target in targets:
        job = queue.enqueue(instaclient.send_dm, user=target, message=message, timeout=120)
    registry:FailedJobRegistry = FailedJobRegistry(queue=queue)
    failed = 0
    while True:
        result = job.result
        if not result:
            # Queue not finished yet
            context.bot.send_message(chat_id=forwarder.chat_id, text=update_scrape_status_text)
            time.sleep(20)
            continue
        else:
            # Result is done
            for job in registry.get_job_ids():
                if job in targets:
                    failed += 1
            context.bot.send_message(chat_id=forwarder.chat_id, text=finished_sending_dm_text.format(failed))
            return True

        
        
        

    


