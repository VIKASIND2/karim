# Karim
This Telegram Bot can connect to the Telegram Client with the user's credentials in order to access the client's functionalities. The bot can forward a select message to all the chat members in a selection of group chats or channels.
The bot is running on Heroku. 

## Bot Commands
Currently, the bot will be able to respond to the following commands:
- ```/account``` -> Returns the current connection status to the Telegram Client (if the user is logged in and with which Telegram Account)
- ```/signin``` -> Asks the user to input Telegram Credentials and attempts to sign in the Telegram Client. No credentials will be stored in the server.
    * ```phone``` -> The user's telegram account's phone number (```+49 123 123 1234```)
    * ```code``` -> The security code sent by Telegram to verify the identity. It is important to send the code separated by dots (```1.2.3.4.5```) otherwise it will immediatelly expire.
    * ```password``` -> In case the user has set a 2-steps-verification password, this will be required to sign in correctly.
- ```/signout``` -> Signs out of the Telegram Client and deletes the session.
- ```/forward``` -> Allows the user to forward a message to all the chat members present in a selection of group chats, via the user's own account.

## Use the Bot
- Create a Heroku Account
- Contact me (@davidwickerhf) and send me your Heroku Email (the email adress you used to create the Heroku account)
    - I will transfer the bot to your account
- Upgrade Heroku Plan
    - The bot is running on a free version of Heroku:
        - Persistence won't work for longer than 30 minutes
        - The Bot is designed to not require a paid Heroku Plan
        - To use the bot, you will need to Sign In (with ```/signin```) every 30 minutes
    - By upgrading your Heroku Plan, the bot will be able to persist and the Telegram Client Sessions will be saved in a database (so you won't have to sign in multiple times)
- Start the Bot
    - Write /start to @KarimLumanBot to start using the bot
- Read the command reference doc: [Bot Commands]()

## Running the Bot Locally
The bot is built on a Flask Python server in order to be compatible for upload to an online server (such as Heroku)
Follow the steps below to run the bot on your local machine. (These steps don't include the steps to install Python)
1. #### Clone the Repository
    clone the master branch of this repository to your local machine
2. #### Install Ngrok
    Install ngrok from [Ngrok](https://ngrok.com/download)
3. #### Setup secrepts.json file
    Create a file named secrets.json in the [secrets](https://github.com/davidwickerhf/karim/tree/main/karim/secrets) folder. This should include:
    ```
    {
    "SERVER_APP_DOMAIN": "", # insert here the https link you will receive from Ngrok in the next steps
    "DEVS": [427293622], 
    "API_ID": , # get this from https://my.telegram.org/apps
    "API_HASH": "", # get this from https://my.telegram.org/apps
    "API_PHONE": "", # insert here your Telegram phone number
    "BOT_TOKEN": "" # insert here the BOT TOKEN
    }
    ```
4. #### Run ngrok 
    Open your command prompt and navigate to the directory where you saved the Ngrok file. Then type: ```ngrok http 5000```
5. #### Run program
    With the command prompt navigate to the directory where you cloned the git repository and run the followinf commands:
    * ```python -m venv env```
    * ```env/Scripts/activate```
    * ```pip install -r requirements.txt```
    * ```python run.py```
    The last command should launch the bot if everything went correctly.
