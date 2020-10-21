from rq.job import Retry
from karim import queue, LOCALHOST, instaclient, testbot
from karim.bot.texts import *

def queue_scrape(target, count, context, forwarder):
    queue.enqueue(instaclient.scrape_followers, user=target, count=count, callback_frequency=count//10, timeout=84000)   

def queue_send_dm(targets, message):
    for target in targets:
        queue.enqueue(instaclient.send_dm, user=target, message=message, timeout=120)

