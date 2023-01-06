import os
from flask import Flask, request, json, render_template
from bots.DataScraper import DataCollector
from twilio.rest import Client
from datetime import datetime,date
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_ENDPOINT = os.getenv('TWILIO_ENDPOINT')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)
app.messages = {}
app.scraper = False
app.shift_preferences = None
app.weekdays = {
	0:"mon",
	1:"tue",
	2:"wed",
	3:"thu",
	4:"fri",
	5:"sat",
	6:"sun",
}

# ---------------------------------------------------------------------------

@app.route('/chickenparm')
def index():
	return render_template("index.html")

# ---------------------------------------------------------------------------

"""
This route is used to gather users 7shifts login information and
	their desired shift preferences
"""
@app.route(f'/submit/{TWILIO_ENDPOINT}', methods=['POST'])
def submit():
	user_data = request.json['account']
	app.shift_preferences = request.json['requested']
	print(app.shift_preferences)
	scraper = DataCollector(*request.json['account']['login'])
	scraper.run()
	if scraper.login_success:
		print("---LOGIN SUCCESS---")
		app.scraper = scraper
		print(f"7shifts User ID: {app.scraper.user_id}")
		twilio_endpoint()
	else:
		print("---LOGIN FAILED---")
	return render_template("index.html")

# ---------------------------------------------------------------------------

"""
The purpose of using a webhook & checking twilio messages instead of 
recurringly querying 7shifts pool data via a loop is to minimize 
web requests sent to their website. This increases speed, decreases memory, 
cpu usage, and the apps footprint especially compared to the prior selenium version.
"""
@app.route(f'/{TWILIO_ENDPOINT}', methods=['POST'])
def twilio_endpoint():
	"""
	This function/route is meant to be called by a twilio webhook when twilio
	receives a new text message. It first checks the days messages for text
	containing a string describing a shift we are looking for.

	If using webhooks is not and option this function can be run in a loop 
	constantly check a twilio accounts received messages. Twilio may block 
	and/or rate limit requests if the api is called to often.
	"""
	# The endpoint will be accessable upon launch. However the scraper
	# 	will not be initialized until a sends a post request to /submit
	#	with login info and desired shift options
	print("---Notification Received---")
	print('Checking Scraper...')
	if not app.scraper:
		print('Scraper not initiated')
		print("---EXITING---")
		return 'Scraper not initiated'
	print('Checking Twilio Messages....')
	messages = client.messages.stream(date_sent=date.today())
	if messages:
		print("Reading Messages....")
	if not validate_sms(messages):
		print("No New Messages....")
		print("---EXITING---")
		return "no new messages"
	# The websites shift data may have change since it was last loaded.
	# Update the necessary data to search for and claim shifts.
	app.scraper.run()
	# Iterate over available shifts
	available_shifts = app.scraper.shift_pool.shifts
	if not available_shifts:
		print('Shift Pool Empty.')
		print("---EXITING---")
		return "No Available Shifts."
	# Look for a shift matching user preferences
	if validate_shifts(available_shifts):
		# Attempt to claim the shift
		if app.scraper.pickup_shift(shift_id):
		# If a shift is claimed then the apps known data needs to be updated
			print('---Shift Claimed---')
			# Keep running and updating known shifts until there are no 
			#	matching shifts left in the pool
			twilio_endpoint()
	print("---EXITING---")
	# Then exit the loop and wait for another twilio callback request
	return 'Search Complete.'

# ---------------------------------------------------------------------------

def validate_shifts(available_shifts:list) -> bool:
	for shift_id in available_shifts:
		shift = app.scraper.shift_pool.shifts[shift_id]
		# Check if the shift role is one the user wants
		if shift.role['name'] not in app.shift_preferences["roles"]:
			print(f'Shift role not {app.shift_preferences["roles"]}\t\t{shift}')
			continue
		# Check if the shift location is one the user wants
		if shift.role['location'] not in app.shift_preferences["locations"]:
			print(f'Shift location not {app.shift_preferences["locations"]}\t\t{shift}')
			continue
		# Parse out the shift date
		shift_date = shift.start.split('T')[0]
		# Convert numeric day into a weekday
		weekday = day_of_week(shift_date)
		# If the weekday somehow ends up not an valid weekday
		if not weekday or weekday not in app.weekdays.keys():
			print('Failed to parse valid weekday from shift_date')
			continue
		# Check if the shift day is one the user wants
		if weekday not in app.shift_preferences["days"]:
			print(f'Shift day not {app.shift_preferences["days"]}\t\t{shift}')
			continue
		# Attempt to convert shift_date into datetime
		try:
			shift_date = datetime.strptime(shift_date, '%Y-%m-%d')
		except:
			print('Could not format shift_date into datetime object')
			continue
		# Gather what days the user is already working on
		user_scheduled_days = [shift.start.day for shift in app.scraper.user_shifts.values()]
		# If user is already scheduled on found shifts date
		if shift_date.day in user_scheduled_days:
			print(f'Already scheduled [{str(shift_date).split(" ")[0]}] \t\t{shift}')
			continue

		# This really shouldn't happen but is here as an extra safety.....
		# If the shift is already assigned to the user
		if shift_id in app.scraper.user_shifts:
			print(f'Already owned: \t\t\t\t{shift}')
			continue
		# If we made it here the found shift is acceptable to claim	
		return True
	return False

# ---------------------------------------------------------------------------

def validate_sms(messages:client.messages) -> bool:
	new_message = False
	for message in messages:
		# only consider messages sent by twilio
		if message.from_ != TWILIO_PHONE_NUMBER:
			print('Message not sent from twilio...... Ignoring')
			continue
		# If the message has already been stored in the app skip to the next message
		if message.sid in app.messages:
			# print("Skipping old message")
			continue
		# If it is a newly seen message
		else:
			# store it to our known messages
			app.messages[message.sid] = message.body
		# Each message describing an available shift will have 'up for grabs' in it.
		# If not then the message was not about a dropped shift and we should ignore it.
		if 'up for grabs' not in message.body:
			print('Not a shift pool message')
			continue
		else:
			print(message.body)
			new_message = True
	else:
		return new_message
	
# ---------------------------------------------------------------------------

def day_of_week(shift_date:str) -> str:
	# shift_date = message_body.replace('.',"").split("on ")[-1]
	d=date.today()
	d=d.replace(day=int(shift_date))
	try:
		shift_date = datetime.strptime(shift_date,"%a, %B %d, %Y").day
	except:
		print(" datetime format failed")
	try:
		shift_date = datetime.strptime(shift_date, '%Y-%m-%d').day
	except:
		print("Second datetime format failed")
		return False
	return app.weekdays[d.weekday()]

# ---------------------------------------------------------------------------

if __name__ == "__main__":
	# Loading users 7shift data into the scraper
	app.scraper = DataCollector()
	app.scraper.run()
	# check new shift data for a shift
	# twilio_endpoint()
	# Launching the callback webserver
	app.run(host="0.0.0.0", port=5007)