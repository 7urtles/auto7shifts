import os
import stripe
import tools.verifications as v

from dotenv import load_dotenv
from threading import Thread
from flask import Flask, request, render_template, url_for, redirect, jsonify

from tools.server_utils import *
from tools.twilio_sms import send_sms
from bot import Shift_Bot, scraper_driver


# -----------------------------------------------------------------------------
load_dotenv()
PUB_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SEC_KEY = os.getenv('STRIPE_SECRET_KEY')
END_KEY = os.getenv('ENDPOINT_SECRET_KEY')
SMS_URL_KEY = os.getenv('SMS_URL_KEY')

stripe.api_key = STRIPE_SEC_KEY

app = Flask(__name__)
scrapers = {}


# -----------------------------------------------------------------------------
# Routes Begin: 
@app.route('/')
def home():
	return render_template('index.html')


# -----------------------------------------------------------------------------
@app.route('/submit', methods = ['POST'])
def submit():
	match request.method:
		case 'POST':
			login_credentials = v.verify_7shifts_login(request)
			if login_credentials:
				scraper = Shift_Bot(login_credentials=login_credentials)
				# scraper.login_credentials = login_credentials
				# if scraper.login_credentials['login_success']:
				store_to_csv(login_credentials)
				scrapers[scraper.login_credentials['email']] = login_credentials['email']
			else:
				return redirect('http://www.7shifts.online/invalid_credentials')
		case _:
			response = 'ERROR: Unsupported Method'
	return redirect('https://buy.stripe.com/test_00g03p6DA2P26ukdQQ') # TEST URL
	# return redirect('https://buy.stripe.com/14kaI43oh9Nm8msaEG') # LIVE PAYMENT URL


# -----------------------------------------------------------------------------
@app.route('/invalid_credentials')
def invalid_credentials():
	return render_template('invalid_credentials.html')


# -----------------------------------------------------------------------------
#@app.route("/checkout")
#def get_publishable_key():
#    return render_template('checkout.html',key=PUB_KEY)


# -----------------------------------------------------------------------------
@app.route("/sms/user_registered/"+SMS_URL_KEY)
def user_registered():
	send_sms('New User Registered')
	return 'sms sent'


# -----------------------------------------------------------------------------
@app.route('/payment_successful', methods=['POST'])
def webhook():
	# check the request data to confirm stripe payment for user
	payment_intent = v.verify_stripe_payment(request, END_KEY)
	if payment_intent: 
		if match_payment_email_to_scraper(payment_intent):
			# if start_scraper(scrapers[email]):
			thread = Thread(target=scraper_driver,args=(scrapers[email]))
			thread.start()
			return redirect('/payment_successful.html')
			# else:
			# 	print(f'ERROR: Issue launching scraper for {email}')
			# 	return(f'ERROR: Issue launching scraper for {email}')
		else:
			print("No scraper instance matching email from payment")
			return("No scraper instance matching email from payment")
	else:
		print("Invalid Payment")
		return("Invalid Payment")

	return 'Unknow errored occurred. Please contact admin via stripe sms service'


# -----------------------------------------------------------------------------
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5007)
	
