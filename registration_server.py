from flask import Flask, request, render_template, url_for, redirect, jsonify
from functools import wraps

import os

import stripe

from dotenv import load_dotenv

from tools.utils import *
from tools.twilio_sms import send_sms
from tools.telegram_bot import send_telegram


load_dotenv()

PUB_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SEC_KEY = os.getenv('STRIPE_SECRET_KEY')
END_KEY = os.getenv('ENDPOINT_SECRET_KEY')
SMS_URL_KEY = os.getenv('SMS_URL_KEY')

stripe.api_key = STRIPE_SEC_KEY

app = Flask(__name__)

# Dynamic url acceptance route
# @app.route('/signup/'+'<url>'', methods = ['POST'])
# Wrapper for creating & validating one time use urls
# @one_time_url
@app.route('/signup')
# @send_routes
def home():
	global expected_urls

	match request.method:
		case 'GET':
			response = render_template('index.html')
		case _:
			response = 'unsupported method'
	return response

# Dynamic url acceptance route
# @app.route('/signup/'+'<url>'+'/submit', methods = ['POST'])
# Wrapper for creating & validating one time use urls
# @one_time_url
@app.route('/submit', methods = ['POST'])
# @send_routes
def submit():
	match request.method:
		case 'POST':
			data = dict(request.form)
			data.update({'time_submitted':datetime.now()})
			store_data(data)
			response = 'Shift request recieved'
		case _:
			response = 'unsupported method'
	return redirect('https://buy.stripe.com/aEU9E04sle3CbyEeUV')

# route to display all active one time use urls
# @app.route('/'+END_KEY)
# @send_routes
# def routes_to_telegram(x):
# 	return 'routes sent'

@app.route("/checkout")
def get_publishable_key():
    return render_template('checkout.html',key=PUB_KEY)

@app.route("/charge",methods=["POST"])
def charge():
	return redirect('https://buy.stripe.com/test_00g03p6DA2P26ukdQQ')
    # return redirect('https://buy.stripe.com/cN22by1g9cZydGM6oo')

@app.route("/sms/user_registered/"+SMS_URL_KEY)
def user_registered():
	send_sms('New User Registered')
	return 'sms sent'

# SUCCESSFUL PAYMENT ENDPOINT
@app.route('/payment_successful', methods=['POST'])
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
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)

if __name__ == "__main__":
	# Generate a new random url string
	# add_url()
	# Add specific url to list of accepted urls
	# add_url(url=END_KEY)
	# Send currently accepted urls in a telegram message
	# send_telegram(urls_to_string())
	app.run(host='0.0.0.0', port=80)
