import os
import logging
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import date

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
ACCOUNT_PHONE_NUMBER = os.getenv('ACCOUNT_PHONE_NUMBER')
TWILIO_ENDPOINT = os.getenv('TWILIO_ENDPOINT')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# ---------------------------------------------------------------------------

def new_shift_sms() -> bool:
    logging.info('Reading Twilio Messages')
    messages = client.messages.stream(date_sent=date.today())
    for message in messages:
        # only consider messages sent by twilio
        # if message.from_ != 7SHIFTS_PHONE_NUMBER:
        #     logging.info('Message not sent from twilio...... Ignoring')
        #     continue
        # If the message has already been stored in the app skip to the next message
        if message.sid in app.messages:
            # logging.info("Skipping old message")
            continue
        # If it is a newly seen message
        else:
            # store it to our known messages
            app.messages[message.sid] = message.body
        # Each message describing an available shift will have 'up for grabs' in it.
        # If not then the message was not about a dropped shift and we should ignore it.
        if 'up for grabs' not in message.body:
            logging.info('Not a shift pool message')
            continue
        else:
            logging.info(message.body)
            return True
    else:
        logging.info("No New Messages")
        return False
# -----------------------------------------------------------------------------

def send_sms(number=ACCOUNT_PHONE_NUMBER, message='shift picked up'):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) 
    # try:
    message = client.messages.create(  
                to = number,
                from_ = TWILIO_PHONE_NUMBER,
                body = message
            ) 
    print(f'SMS SENT: {number}')
