from karim import LOCALHOST
from gspread.models import Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import json
from datetime import datetime
from karim.secrets import secrets



def auth():
    if not (os.path.isfile('movement_assistant/secrets/sheet_token.pkl') and os.path.getsize('movement_assistant/secrets/sheet_token.pkl') > 0):
        # use creds to create a client to interact with the Google Drive API
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive']
        # CREDENTIALS HAVE NOT BEEN INITIALIZED BEFORE
        client_secret = os.environ.get('GCLIENT_SECRET')
        if LOCALHOST:
            # CODE RUNNING LOCALLY
            print('DATABASE: Resorted to local JSON file')
            with open('movement_assistant/secrets/client_secret.json') as json_file:
                client_secret_dict = json.load(json_file)
        else:
            # CODE RUNNING ON SERVER
            client_secret_dict = json.loads(client_secret)

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            client_secret_dict, scope)
        creds_string = json.dumps(creds)
        secrets.set_var('GSPREAD_CREDS', creds_string)

    creds = json.loads(secrets.get_var('GSPREAD_CREDS'))
    client = gspread.authorize(creds)

    # IF NO SPREADSHEET ENV VARIABLE HAS BEEN SET, SET UP NEW SPREADSHEET
    if secrets.get_var('SPREADSHEET') == None:
        spreadsheet = set_sheet(client)
        return spreadsheet
    else:
        SPREADSHEET = secrets.get_var('SPREADSHEET')
        spreadsheet = client.open_by_key(SPREADSHEET)
        return spreadsheet


def log(timestamp, user_id, action):
    spreadsheet = auth()
    logs = spreadsheet.get_worksheet(2)                     
    logs.append_row([timestamp, user_id, action])


def add_subscriber(id):
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    subscribers.append_row([id])
    # LOG
    log(datetime.utcnow(), id, 'SUBSCRIBE')
    

def remove_subscriber(id):
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    try: subscribers.delete_row(find_row_by_id(item_id=id)[0])
    except: pass
    # LOG
    log(datetime.utcnow(),id, 'UNSUBSCRIBE')


def is_subscriber(id):
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    rows = find_row_by_id(id, sheet=subscribers)[0]
    if not rows:
        return False
    else:
        return True


def get_subscribers():
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    rows = get_all_rows(subscribers)
    return rows


def add_scrape(user_id, name, scraped):
    string_scraped = str(scraped)
    string_scraped = string_scraped.replace('[', '')
    string_scraped = string_scraped.replace(']', '')
    spreadsheet = auth()
    scraped = spreadsheet.get_worksheet(1)
    last_scrape = find_row_by_id(user_id, scraped)
    if not last_scrape[0]:
        scraped.append_row([user_id, name, string_scraped])
        # TODO ADD SCRAPED IF SELECTION IS ALREADY IN DATABASEs


def find_row_by_id(item_id, sheet, col=1):
    print("DATABASE: find_row_by_id()")
    if not sheet:
        spreadsheet = auth()
        sheet = spreadsheet.get_worksheet(0)
    column = sheet.col_values(col)
    rows = []
    for num, cell in enumerate(column):
        if str(cell) == str(item_id):
            rows.append(num + 1)
    if rows == []:
        rows.append(None)
    return rows


def get_all_rows(sheet):
    if not sheet:
        spreadsheet = auth()
        sheet = spreadsheet.get_worksheet(0)
    rows = sheet.get_all_values()
    simplified = []
    for row in rows:
        simplified.append(row[0])
    return rows


""" def clean_sheet(sheet):
    rows = find_row_by_id(item_id='')
    for row in reversed(rows):
        if row in (None, ''):
            try: sheet.delete_row(find_row_by_id(item_id=id)[0])
            except: pass """



def set_sheet(client):
    """
    Setup spreadsheet database if none exists yet.
    Will save the spreadsheet ID to Heroku Env Variables
    The service email you created throught the Google API will create the new spreadsheet and share it with the email you indicated in the GDRIVE_EMAIL enviroment variable. You will find the spreadsheet database in your google drive shared folder.
    Don't change the order of the worksheets or it will break the code.
    """
    # CREATE SPREADSHEET
    spreadsheet = client.create('KARIM MAILINGLIST')
    secrets.set_var('SPREADSHEET', spreadsheet.id)

    # CREATE GROUP CHATS SHEET
    subscribers = spreadsheet.add_worksheet(title="Subscribers", rows="150", cols="1")
    scraped = spreadsheet.add_worksheet(title='IG Scraped', rows = '150', cols='3')

    # CREATE LOGS SHEET
    logs = spreadsheet.add_worksheet(title="Logs", rows="500", cols="3")
    logs.append_row(["TIMESTAMP", "USER ID", "ACTION"])

    # DELETE PRE-EXISTING SHEET
    sheet = spreadsheet.get_worksheet(0)
    spreadsheet.del_worksheet(sheet)

    # SHARE SPREADSHEET
    spreadsheet.share(value=secrets.get_var('GDRIVE_EMAIL'),
                      perm_type="user", role="owner")
    return spreadsheet