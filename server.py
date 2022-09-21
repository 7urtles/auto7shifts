import os
from dotenv import load_dotenv

from flask import Flask, request, render_template, url_for, redirect, jsonify

import stripe

from tools.server_utils import *
from tools.twilio_sms import send_sms
from auto_pickup_7shifts import Shift_Grabber, scraper_driver

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
			registration_data = dict(request.form)
			scraper = Shift_Grabber(login_credentials=registration_data)
			scraper.login_credentials.update({
				'time_submitted':datetime.now(), 
				"login_success":scraper.login()
			})
			if scraper.login_credentials['login_success']:
				store_to_csv(scraper.login_credentials)
				scrapers[scraper.login_credentials['email']] = scraper
			else:
				return redirect('http://www.7shifts.online/invalid_credentials')

		case _:
			response = 'ERROR: Unsupported Method'
	#return redirect('https://buy.stripe.com/test_00g03p6DA2P26ukdQQ') # TEST URL
	return redirect('https://buy.stripe.com/14kaI43oh9Nm8msaEG') # LIVE PAYMENT URL


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
@app.route('/payment_successful', methods=['GET','POST'])
def webhook():
	event = None
	payload = request.data
	sig_header = request.headers['STRIPE_SIGNATURE']

	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, END_KEY
			)
	except ValueError as e:
		# Invalid payload
		raise e

	except stripe.error.SignatureVerificationError as e:
		# Invalid signature
		raise e

    # Handle the event
	if event['type'] == 'payment_intent.succeeded':
		payment_intent = event['data']['object']
		print('payment succeeded')

		if match_payment_to_registered_user(payment_intent):
			if start_scraper(scrapers[email]):
				scraper_driver(scrapers[email])
				return redirect('/payment_successful.html')
			else:
				print(f'ERROR: Issue launching scraper for {email}')
		
    # ... handle other event types
	else:
		print('Unhandled event type {}'.format(event['type']))
		return "Oops! Something went wrong"


# -----------------------------------------------------------------------------
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5007)
	
