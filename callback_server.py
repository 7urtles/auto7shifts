import os
import logging
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
	logging.info(app.shift_preferences)
	scraper = DataCollector(*request.json['account']['login'])
	scraper.run()
	if scraper.login_success:
		logging.info("---LOGIN SUCCESS---")
		app.scraper = scraper
		logging.info(f"7shifts User ID: {app.scraper.user_id}")
		twilio_endpoint()
	else:
		logging.info("---LOGIN FAILED---")
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
	logging.info("---Notification Received---")
	logging.info('Checking Scraper...')
	if not app.scraper:
		logging.info('Scraper not initiated')
		logging.info("---EXITING---")
		return 'Scraper not initiated'
	logging.info('Checking Twilio Messages....')
	messages = client.messages.stream(date_sent=date.today())
	if messages:
		logging.info("Reading Messages....")
	if not validate_sms(messages):
		logging.info("No New Messages....")
		logging.info("---EXITING---")
		return "no new messages"
	# The websites shift data may have change since it was last loaded.
	# Update the necessary data to search for and claim shifts.
	app.scraper.run()
	# Iterate over available shifts
	available_shifts = app.scraper.shift_pool.shifts
	logging.debug(available_shifts)
	if not available_shifts:
		logging.info('Shift Pool Empty.')
		logging.info("---EXITING---")
		return "No Available Shifts."
	# Look for a shift matching user preferences
	logging.debug("Checking shifts for match.")
	found_shift_id = validate_shifts(available_shifts)
	if found_shift_id:
		# Attempt to claim the shift
		if app.scraper.pickup_shift(found_shift_id):
		# If a shift is claimed then the apps known data needs to be updated
			logging.info('---Shift Claimed---')
			# Keep running and updating known shifts until there are no 
			#	matching shifts left in the pool
			twilio_endpoint()
	logging.info("---EXITING---")
	# Then exit the loop and wait for another twilio callback request
	return 'Search Complete.'

# ---------------------------------------------------------------------------

def validate_shifts(available_shifts:list) -> str:
	for shift_id in available_shifts:
		logging.debug(f"Checking shift: {shift_id}")
		shift = app.scraper.shift_pool.shifts[shift_id]
		logging.debug(shift)
		# Check if the shift role is one the user wants
		if shift.role['name'] not in app.shift_preferences["roles"]:
			logging.debug(shift.role['name'])
			logging.info(f'Shift role not {app.shift_preferences["roles"]} {shift}')
			continue
		# Check if the shift location is one the user wants
		if shift.role['location'] not in app.shift_preferences["locations"]:
			logging.debug(shift.role['location'])
			logging.info(f'Shift location not {app.shift_preferences["locations"]} {shift}')
			continue
		# Parse out the shift date
		shift_date = shift.start.split('T')[0]
		# Convert numeric day into a weekday
		weekday = day_of_week(shift_date)
		logging.debug(f"Shift day of week: {weekday}")
		# If the weekday somehow ends up not an valid weekday
		if not weekday or weekday not in app.weekdays.keys():
			logging.info('Failed to parse valid weekday from shift_date')
			continue
		# Check if the shift day is one the user wants
		if weekday not in app.shift_preferences["days"]:
			logging.debug(f"{weekday} not in {app.shift_preferences['days']}")
			logging.info(f"Shift day not {app.shift_preferences['days']} {shift}")
			continue
		# Attempt to convert shift_date into datetime
		try:
			shift_date = datetime.strptime(shift_date, '%Y-%m-%d')
		except:
			logging.info('Could not format shift_date into datetime object')
			continue
		# Gather what days the user is already working on
		user_scheduled_days = [shift.start.day for shift in app.scraper.user_shifts.values()]
		# If user is already scheduled on found shifts date
		if shift_date.day in user_scheduled_days:
			logging.info(f'Already scheduled [{str(shift_date).split(" ")[0]}] {shift}')
			continue

		# This really shouldn't happen but is here as an extra safety.....
		# If the shift is already assigned to the user
		if shift_id in app.scraper.user_shifts:
			logging.info(f'User already working this shift {shift}')
			continue
		# If we made it here the found shift is acceptable to claim	
		return shift_id
	return False

# ---------------------------------------------------------------------------

def validate_sms(messages:client.messages) -> bool:
	new_message = False
	for message in messages:
		# only consider messages sent by twilio
		if message.from_ != TWILIO_PHONE_NUMBER:
			logging.info('Message not sent from twilio...... Ignoring')
			continue
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
		logging.info("Datetime format failed")
	try:
		shift_date = datetime.strptime(shift_date, '%Y-%m-%d').day
	except:
		logging.info("Second datetime format failed")
		return False
	return app.weekdays[d.weekday()]

# ---------------------------------------------------------------------------

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	# Loading users 7shift data into the scraper
	app.scraper = DataCollector()
	app.scraper.run()
	# check new shift data for a shift
	# twilio_endpoint()
	# Launching the callback webserver
	app.run(host="0.0.0.0", port=5007)
	# logging.debug('This message should go to the log file')
	# logging.info('So should this')
	# logging.warning('And this, too')
	# logging.error('And non-ASCII stuff, too, like Øresund and Malmö')