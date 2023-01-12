import logging
from dotenv import load_dotenv

from flask import Flask, request, json, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

from scraper import ShiftScraper
from tools.shift_tools import *
from tools.sms_tools import *

# *******************************************************************************
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jdhfalioy4879tyhaw7h4p98w'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

USER_AGENT = os.getenv('USER_AGENT')
# *******************************************************************************
app.scraper = False
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
	shift_handler(app.scraper.shift_pool())
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
	scraper = ShiftScraper(*request.json['account']['login'])
	
	if scraper.login():
		app.scraper = scraper
	
	logging.info("EXITING")
	return "success"

# ---------------------------------------------------------------------------

def shift_handler(pool_data:list[dict]) -> bool:
	"""
	Iterates a list of shifts, formatting their data and checking
	for one that matches the users requirements.
	"""
	logging.info("Checking Shifts")
	for shift in pool_data:
		# clean up excessive dict
		shift = format_shift(shift)
		# convert to obj for easier handling/storage
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

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)

# *******************************************************************************
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

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
	logging.basicConfig(
		format='[%(asctime)s][%(levelname)s][%(name)s]%(filename)s[%(lineno)d]:%(funcName)s() -> %(message)s', 
		filename='logs/7shifts.log', encoding='utf-8', level=logging.DEBUG, 
		datefmt='%m/%d/%Y %I:%M:%S %p'
	)
	b
	# Launching the callback webserver
	app.run(host="0.0.0.0", port=5007)