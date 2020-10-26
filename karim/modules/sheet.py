from gspread.client import Client
import jsonpickle
from karim import LOCALHOST
from gspread.models import Spreadsheet, Worksheet
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import json
from datetime import datetime
from karim.secrets import secrets



def auth():
    creds_string = secrets.get_var('GSPREAD_CREDS')
    if creds_string == None:
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
        creds_string = jsonpickle.encode(creds)
        secrets.set_var('GSPREAD_CREDS', creds_string)
    creds = jsonpickle.decode(creds_string)
    client = gspread.authorize(creds)

    # IF NO SPREADSHEET ENV VARIABLE HAS BEEN SET, SET UP NEW SPREADSHEET
    if secrets.get_var('SPREADSHEET') == None:
        spreadsheet = set_sheet(client)
        return spreadsheet
    else:
        SPREADSHEET = secrets.get_var('SPREADSHEET')
        spreadsheet = client.open_by_key(SPREADSHEET)
        return spreadsheet


def log(timestamp:datetime, user_id:int or str, action:str):
    spreadsheet = auth()
    logs = spreadsheet.get_worksheet(2)                     
    logs.append_row([str(timestamp), user_id, action])


def add_subscriber(id:int or str):
    """
    Add subscriber's id to the GSheet database

    :param id: Telegram id of the user
    :type id: intorstr
    """
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    subscribers.append_row([id])
    # LOG
    log(datetime.utcnow(), id, 'SUBSCRIBE')
    

def remove_subscriber(id:int or str):
    """
    Attempt to remove a subscriber from the newsletter's database

    :param id: Telegram id of the user
    :type id: intorstr
    :return: True if subscriber has been deleted successfully, False is an error occurs
    :rtype: boolean
    """
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    row = find_by_username(username=str(id), sheet=subscribers)[0]
    print('ROW: ', row)
    subscribers.delete_row()
    # LOG
    log(datetime.utcnow(),id, 'UNSUBSCRIBE')
    return True

def is_subscriber(id:int or str):
    """
    is_subscriber [summary]

    [extended_summary]

    :param id: [description]
    :type id: intorstr
    :return: True if id is found, False if id does not exist
    :rtype: boolean
    """
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    rows:int = find_by_username(str(id), sheet=subscribers)
    if str(id) in rows:
        return False
    else:
        return True


def get_subscribers():
    """
    Get a list of Telegram ids of the subscribers of the newsletter

    :return: List of Telegram ids of the subscribers
    :rtype: list
    """
    spreadsheet = auth()
    subscribers = spreadsheet.get_worksheet(0)
    rows:list = get_rows(subscribers)
    simplified = []
    for row in rows:
        simplified.append(row[0])
    return simplified



def add_scrape(username:str, name:str, scraped:list):
    """
    Adds a new row in the Google Sheets Database with the username, name and scraped follower's usernames.
    Extends the scraped list of an already existing entry if the username is already in the database.

    :param username: The username of the user
    :type username: str
    :param name: The name of the scraped selection (can be custumed by user)
    :type name: str
    :param scraped: List of usernames of the user's followers
    :type scraped: list
    """
    string_scraped = str(scraped)
    string_scraped = string_scraped.replace('[', '')
    string_scraped = string_scraped.replace(']', '')
    spreadsheet = auth()
    sheet:Worksheet = spreadsheet.get_worksheet(1)
    last_scrape = find_by_username(username, sheet)
    if not last_scrape[0]:
        sheet.append_row([username, name, string_scraped])
    else:
        values = get_by_username(username)
        followers_str = values[2]
        followers = list(followers_str)
        for item in scraped: 
            if item not in followers:
                followers.append(item)
        sheet.delete_row(last_scrape)
        sheet.append_row([username, name, str(followers)])


def get_targets(username:str):
    """
    Return the scraped username of the followers of a user matching the username - and present in the GSheet Database.

    :param username: Username to look up in the database
    :type username: str
    :return: List of usernames (str) of the followers of the user
    :rtype: list
    """
    scraped = get_by_username(username)
    targets_str = scraped[2]
    targets:list = list(targets_str)
    return targets


def get_all_scraped():
    """
    Get a list of the rows' content from the Google Sheets database.

    :return: List of lists, where each sub-list contains a row's contents.
    :rtype: list
    """
    spreadsheet = auth()
    sheet:Worksheet = spreadsheet.get_worksheet(1)
    scraped = get_rows(sheet)
    return scraped


def get_scraped(username:str):
    """
    Get the information of a scraped selection matching the username

    :param username: The userename to look up for
    :type username: str
    :return: List containing the scrape selection's information | None
    :rtype: list | None
    """
    scraped:list = get_all_scraped()
    for item in scraped:
        if item[0] == username:
            return item
    return None


def find_by_username(username:str, sheet:Worksheet, col:int=1):
    """
    Return the GSheet index of the row matching the username.

    :param username: The username to match
    :type username: str
    :param sheet: The GSheet worksheet to get data from
    :type sheet: Worksheet
    :param col: Column to look up for matching, defaults to 1
    :type col: int, optional
    :return: List of indexes of the rows that match the username
    :rtype: list
    """
    if not sheet:
        spreadsheet = auth()
        sheet = spreadsheet.get_worksheet(0)
    column = sheet.col_values(col)
    print('COLUMN: ', column)
    rows = []
    for num, cell in enumerate(column):
        print('Row value: ', cell)
        if str(cell) == str(username):
            rows.append(num + 1)
    if rows == []:
        rows.append(None)
    return rows


def get_by_username(username:str, sheet:Worksheet):
    """
    Return the contents of the GSheet Database row matching the username.

    :param username: The username to match
    :type username: str
    :param sheet: GSheet worksheet to get data from
    :type sheet: Worksheet
    :return: A list with the contents of the row matching the username
    :rtype: list
    """
    row = find_by_username(username, sheet)[0]
    rows = get_rows(sheet)
    return rows[row+1]


def get_rows(sheet:Worksheet):
    """
    Get a list of the rows' content from the Google Sheets database.

    :param sheet: GSheets worksheet to get data from
    :type sheet: Worksheet

    :return: List of lists, where each sub-list contains a row's contents.
    :rtype: list
    """
    rows:list = sheet.get_all_values()
    return rows


def get_sheet_url():
    spreadsheet = auth()
    sheet:Worksheet = spreadsheet.get_worksheet(0)
    return sheet.url


""" def clean_sheet(sheet):
    rows = find_row_by_id(item_id='')
    for row in reversed(rows):
        if row in (None, ''):
            try: sheet.delete_row(find_row_by_id(item_id=id)[0])
            except: pass """



def set_sheet(client:Client):
    """
    Setup spreadsheet database if none exists yet.
    Will save the spreadsheet ID to Heroku Env Variables or to secrets.json file
    The service email you created throught the Google API will create the new spreadsheet and share it with the email you indicated in the GDRIVE_EMAIL enviroment variable. You will find the spreadsheet database in your google drive shared folder.
    Don't change the order of the worksheets or it will break the code.

    :param client: GSpread client to utilize
    :type client: Client
    :return: The newly created spreadsheet
    :rtype: Spreadsheet
    """
    # CREATE SPREADSHEET
    spreadsheet:Spreadsheet = client.create('KARIM NEWSLETTER')
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