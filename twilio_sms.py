import os

from dotenv import load_dotenv
from twilio.rest import Client 

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_MESSAGING_SERVICE_SID = os.getenv('TWILIO_MESSAGING_SERVICE_SID')
ACCOUNT_PHONE_NUMBER = os.getenv('ACCOUNT_PHONE_NUMBER')

def send_sms(number=ACCOUNT_PHONE_NUMBER, message='success'):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) 
     
    message = client.messages.create(  
                messaging_service_sid = TWILIO_MESSAGING_SERVICE_SID,       
                to = number,
                body = message
            ) 
    print(message.sid)
