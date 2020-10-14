import os
from rq import Queue
from worker import conn

LOCALHOST = True
if os.environ.get('PORT') in (None, ""):
    # Code running locally
    LOCALHOST = True
    if not os.path.exists('karim/bot/persistence'):
        os.makedirs('karim/bot/persistence')
else:
    LOCALHOST = False
    queue = Queue(connection=conn)

