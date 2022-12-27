import os
from flask import Flask, request, json
from bots.DataScraper import DataCollector
from twilio.rest import Client
from datetime import datetime,date
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
EMAIL = os.getenv('CHARLES_EMAIL')
PASSWORD = os.getenv('CHARLES_PASSWORD')
USER_AGENT = os.getenv('USER_AGENT')
CALLBACK_ENDPOINT_URL = os.getenv('CALLBACK_ENDPOINT_URL')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)
app.messages = {}
app.scraper = DataCollector(EMAIL, PASSWORD, USER_AGENT)
app.days = ['Thu','Fri','Sat']
app.roles = ['Bartender']
app.weekday_key = {
	0:"Mon",
	1:"Tue",
	2:"Wed",
	3:"Thu",
	4:"Fri",
	5:"Sat",
	6:"Sun",
}

"""
The purpose of using a webhook & checking twilio messages instead of 
recurringly querying 7shifts pool data via a loop is to minimize 
web requests sent to their website. This increases speed, decreases memory, 
cpu usage, and the apps footprint especially compared to the prior selenium version.
"""

@app.route(f'/{CALLBACK_ENDPOINT_URL}', methods=['POST'])
def twilio_callback():
	"""
	This function/route is meant to be called by a twilio webhook when twilio
	receives a new text message. It first checks the days messages for text
	containing a string describing a shift we are looking for.

	If using webhooks is not and option this function can be run in a loop 
	constantly check a twilio accounts received messages. Twilio may block 
	and/or rate limit requests if the api is called to often.
	"""
	# Checking twilios received texts from 7shifts sms notifications for a qualifying shift
	if check_twilio():
		# The websites shift data may have change since it was last loaded.
		# The below two calls update the necessary data to search for and claim shifts.
		app.scraper.update_shift_pool()
		app.scraper.update_employee_shifts()
		# Iterate over available shifts
		for shift_id in app.scraper.shift_pool.shifts:
			# If a desired shift has not been found
			if not validate_shift(shift_id):
				continue
			# Attempt to claim the shift
			if app.scraper.pickup_shift(shift_id):
			# If a shift is claimed then the apps known data needs to be updated
				print('Updating app data')
				twilio_callback()
		# Then exit the loop and wait for another twilio callback request
	return 'new messages read successfully'

def validate_shift(shift_id) -> bool:
	shift = app.scraper.shift_pool.shifts[shift_id]
	# Check if the shift role is one the user wants
	if shift.role['name'] not in app.roles:
		print(f'Shift role not {app.roles}\t\t{shift}')
		return

	# Parse out the shift date
	shift_date = shift.start.split('T')[0]
	# Convert numeric day into a weekday
	weekday = get_weekday(shift_date)
	# Check if the shift day is one the user wants
	if weekday not in app.days:
		print(f'Shift day not {app.days}\t\t{shift}')
		return
	shift_date = datetime.strptime(shift_date, '%Y-%m-%d')
	# Gather what days the user is already working on
	user_scheduled_days = [shift.start.day for shift in app.scraper.user_shifts.values()]
	# If user is already scheduled on found shifts date
	if shift_date.day in user_scheduled_days:
		print(f'Already scheduled [{str(shift_date).split(" ")[0]}] \t\t{shift}')
		return False

	# This really shouldn't happen but is here as an extra safety.....
	# If the shift is already assigned to the user
	if shift_id in app.scraper.user_shifts:
		print(f'Already owned: \t\t\t\t{shift}')
		return False
	# If we made it here the found shift is acceptable to claim	
	return True

def check_twilio(seven_shifts_sms_number='(201) 627-9226') -> bool:
	"""
	Pulls received text messages from twilio.
	These messages contain a string describing a dropped shifts shift data.
	Checks the messages body string for the users criteria then returns a bool
	describing whether or not a desired shift has been read from the days messages.
	"""
	# to know if the below loop has found a message describing a shift we want
	potential_shift_found = False
	# pull and iterate a twilio accounts received texts from today
	print('Checking Twilio Messages:')
	for message in client.messages.stream(date_sent=date.today()):
		# If the message has already been stored in the app skip to the next message
		if message.sid in app.messages:
			# print("Message already read")
			continue
		# If it is a newly seen message
		else:
			# store it to our known messages
			app.messages[message.sid] = message.body
			
		# Each message describing an available shift will have 'up for grabs' in it.
		# If not then the message was not about a dropped shift and we should ignore it.
		if 'up for grabs' not in message.body:
			print('Found message does not describe a shift')
			continue

		# Format the message body string
		body = message.body.split("grabs:")[1].strip()
		body = body.replace(')',"").split('(')[1]
		# Extract shift role from message body
		role = body.split(' ')[0]

		# Check if role is not one we're looking for
		if role not in app.roles:
			print(f'Shift role not in {app.roles}\t\t{body}')
			# move on to the next message
			continue

		# Extract the date as a string from the message body
		shift_date = body.replace('.',"").split("on ")[-1]
		# Get the day of the week the shift is on
		weekday = get_weekday(shift_date)

		# If it's a day we're not looking for
		if weekday not in app.days:
			print(f'Shift day not in {app.days}\t\t\t{body}')
			# move on to the next message
			continue
		
		# If we've made it this far then make the function aware that a potential shift has been found
		potential_shift_found = True
	# The retreived messages have all been checked
	return potential_shift_found

def get_weekday(shift_date:str) -> str:
	# shift_date = message_body.replace('.',"").split("on ")[-1]
	try:
		shift_date = datetime.strptime(shift_date,"%a, %B %d, %Y").day
	except:
		shift_date = datetime.strptime(shift_date, '%Y-%m-%d').day
	d=date.today()
	d=d.replace(day=int(shift_date))
	return app.weekday_key[d.weekday()]

if __name__ == "__main__":
	# Loading users 7shift data into the scraper
	app.scraper.run()
	twilio_callback()
	# Launching the callback webserver
	# app.run(host="0.0.0.0", port=5007)