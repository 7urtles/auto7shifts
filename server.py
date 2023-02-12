import logging
from dotenv import load_dotenv

from flask import Flask, request, json, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

from scraper import SessionInstance
from tools.shift_tools import *
from tools.sms_tools import *

import requests
# *******************************************************************************
app = Flask(__name__)
# csrf = CSRFProtect(app)

app.config['SECRET_KEY'] = 'jdhfalioy4879tyhaw7h4p98w'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

USER_AGENT = os.getenv('USER_AGENT')
# *******************************************************************************
app.scraper = False
app.scrapers = {}
app.shift_preferences = None

app.messages = {}
# *******************************************************************************

@app.route(f'/{TWILIO_ENDPOINT}', methods=['POST'])
def twilio_endpoint():
	"""
	Called when twilio receives a new text message.
	Checks various criteria to check if there is an available shift the user wants.
	Aattempts to claim the shift if so.
	"""
	logging.info("CALLBACK RECEIVED")
	# Exit if scraper not initialized
	if not app.scraper:
		logging.error('Scraper not initiated')
		logging.info("EXITING")
		return "error"

	# Get updated shift pool and process the found shifts
	app.scraper.update()
	shift_selector(app.scraper.shift_pool)
	# Exit the loop and wait for another twilio callback
	logging.info("EXITING")
	return 'success'

# -------------------------------------------------------------------------

@app.route(f'/submit/{TWILIO_ENDPOINT}', methods=['POST'])
def submit():
	"""
	Gathers users 7shifts login information and shift preferences 
	from a form.
	"""
	logging.info("FORM RECEIVED")
	user_data = request.json['account']
	app.shift_preferences = request.json['requested']
	logging.debug(app.shift_preferences)
	# scraper = LoginInstance(*request.json['account']['login'])
	
	# if scraper.login():
	# 	app.scraper = scraper
	login_request_data = {
		'url':'https://app.7shifts.com/users/login',
		'data':{
			'_method': 'POST',
			'data[User][email]': self.email,
			'data[User][password]': self.password,
			'data[User][keep_me_logged_in]': [
				'0',
				'1',
			],
		},
		'allow_redirects':False
	}
	response = requests.post(**login_request_data)
	logging.info("EXITING")
	return str(response.status_code)

# ---------------------------------------------------------------------------

def shift_selector(pool_data:list[dict]) -> bool:
	"""
	Iterates a list of shifts, formatting their data and checking
	for one that matches the users requirements.
	"""
	if not pool_data:
		return False
	logging.info("Checking Shifts")
	for shift in pool_data:
		# remove unwanted dict values
		shift = format_shift(shift)
		# create shift obj from dict for more simple handling/storage
		shift = DroppedShift(**shift)
		# if shift is new to the database
		if shift_not_stored(shift.id):
			# store it
			store_shift(shift)
		# If user wants the shift
		if shift_wanted(shift, app):
			# take it
			app.scraper.pickup_shift(shift.id)
			send_sms(message=f"Shift Picked Up:\n{shift.role} {shift.day} {shift.location}")
			return True
	return False
# ---------------------------------------------------------------------------
		
class DroppedShift(db.Model):
    db_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    day = db.Column(db.String(20), nullable=False)
    shift_pool_id = db.Column(db.Integer, nullable=False)
    shift_offer_id = db.Column(db.Integer, nullable=False)
    start = db.Column(db.String(80), nullable=False)
    end = db.Column(db.String(80), nullable=False)
    open = db.Column(db.String(80), nullable=False)
    user = db.Column(db.Integer, nullable=False)
    locationId = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    def __repr__(self) -> str:
        return f"<Shift:{self.id} | {self.role['name']} | {self.location['address'].split(' ')[0]} | {self.start.split('T')[0]} | PoolID:{self.shift_pool_id}>"


# ---------------------------------------------------------------------------
def init_db():
	with app.app_context():
		db.create_all()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
	init_db()
	logging.basicConfig(
		format='[%(asctime)s][%(levelname)s][%(name)s]%(filename)s[%(lineno)d]:%(funcName)s() -> %(message)s', 
		#filename='logs/7shifts.log', 
		encoding='utf-8',
		level=logging.DEBUG, 
		datefmt='%m/%d/%Y %I:%M:%S %p'
	)
	# Launching the callback webserver
	app.run(host="0.0.0.0", port=5007)
