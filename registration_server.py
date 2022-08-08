from flask import Flask, request, render_template, url_for, redirect, jsonify
from functools import wraps

import os

import stripe

from utils import *
from telegram_bot import send_message

from dotenv import load_dotenv

load_dotenv()

PUB_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
SEC_KEY = os.getenv('STRIPE_SECRET_KEY')
END_KEY = OS.GETENV('ENDPOINT_SECRET_KEY')

stripe.api_key = SEC_KEY
print(f"{PUB_KEY}\n{SEC_KEY}")

app = Flask(__name__)


@app.route('/signup/'+'<url>')
@one_time_url
@send_routes
def home(url):
	global expected_urls

	match request.method:
		case 'GET':
			response = render_template('index.html')
		case _:
			response = 'unsupported method'
	return response

@app.route('/signup/'+'<url>'+'/submit', methods = ['POST'])
@one_time_url
@send_routes
def submit(url):
	match request.method:
		case 'POST':
			data = dict(request.form)
			data.update({'time_submitted':datetime.now()})
			store_data(data)
			response = 'Shift request recieved'
		case _:
			response = 'unsupported method'
	return redirect('https://buy.stripe.com/test_00g03p6DA2P26ukdQQ')


@app.route('/jkdfal84375ry9thgiu')
@send_routes
def routes_to_telegram(x):
	return 'routes sent'

@app.route("/config")
def get_publishable_key():
    return render_template('checkout.html',key=PUB_KEY)

@app.route("/charge",methods=["POST"])
def charge():
	return redirect('https://buy.stripe.com/test_00g03p6DA2P26ukdQQ')
    # return redirect('https://buy.stripe.com/cN22by1g9cZydGM6oo')


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
	add_url()
	add_url(url='jkdfal84375ry9thgiu')
	send_message(urls_to_string())
	app.run(host='0.0.0.0', port=80)
