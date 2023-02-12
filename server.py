import logging
from dotenv import load_dotenv

from flask import Flask, request, json, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# from flask_wtf import FlaskForm
# from flask_wtf.csrf import CSRFProtect
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import DataRequired, EqualTo

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
			'data[User][email]': 'charleshparmley@gmail.com',
			'data[User][password]': 'Earthday19!@22',
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

"""
# WIP
# for web ui access and interface

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    form = RegistrationForm()
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
---------------------------------------------------------------------------


class RegistrationForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
---------------------------------------------------------------------------
"""


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Employee(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(80))
	lastname = db.Column(db.String(80))
	birth_date = db.Column(db.String(80))
	email = db.Column(db.String(80), unique=True, nullable=False)
	photo = db.Column(db.String(80))
	mobile_phone = db.Column(db.String(80))
	employee_id = db.Column(db.Integer)
	notes = db.Column(db.String(80))
	address = db.Column(db.String(80))
	appear_as_employee = db.Column(db.Boolean())
	active = db.Column(db.Boolean())
	company_id = db.Column(db.String(80))

	def __repr__(self) -> str:
		return f"<Employee {self.id}>\n{self.firstname}\n{self.email}"
		
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


def request_employees():
	shift_scraper = SessionInstance('charleshparmley@icloud.com', 'Earthday19!@22')
	shift_scraper.update()
	return shift_scraper.update_employee_data()

	
def write_employees(employees):
	for employee in employees.values():
		emp = Employee(**employee)
		employee_in_db = Employee.query.filter_by(email = emp.email).first()
		if not employee_in_db:
			db.session.add(Employee(**employee))
			db.session.commit()
		else:
			logging.debug("Employee already exists")
	return True

def read_employees():
	for employee in Employee.query.all():
		print(f"{employee}\n")
	return True

def init_db():
	
	with app.app_context():
		db.create_all()

		employees = request_employees()
		write_employees(employees)
		read_employees()
		exit()
		
		
		shift_scraper = SessionInstance('charleshparmley@icloud.com', 'Earthday19!@22')
		shift_scraper.update()



		

# ---------------------------------------------------------------------------
if __name__ == "__main__":
	from pprint import pprint as pp

	init_db()
	
	exit()
	
	logging.basicConfig(
		format='[%(asctime)s][%(levelname)s][%(name)s]%(filename)s[%(lineno)d]:%(funcName)s() -> %(message)s', 
		#filename='logs/7shifts.log', 
		encoding='utf-8',
		level=logging.DEBUG, 
		datefmt='%m/%d/%Y %I:%M:%S %p'
	)
	# Launching the callback webserver
	app.run(host="0.0.0.0", port=5007)
