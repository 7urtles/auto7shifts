import os
import json, csv
import socket

from flask import Flask, request, render_template, url_for, redirect
from functools import wraps
from random import choices
from string import ascii_lowercase
# import telegram_bot.send_message
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase


global ip
global expected_urls
global telegram_bot_subnet

telegram_bot_subnet = '149.154.161'
ip = 'www.7shifts.online'
expected_urls = []




# -----------------------------------------------------------------------------
def match_payment_to_registered_user(email):
	if email in scrapers:
		return True
	else:
		print(f'ERROR: Payment email: {email} not found in registered scrapers.')
		return False


# -----------------------------------------------------------------------------
def start_scraper(scraper):
	print('launching scraper')
	if scrapers[email].run():
		print(f'Scraper for user: {scraper} running')
		return True
	else:
		print('ERROR: Scraper not started')
		return False


def block_ip(req):
	return True if telegram_bot_subnet in req.remote_addr else False


def send_routes(func):
	global expected_urls
	global ip
	@wraps(func)
	def decorated_function(url=None):
		message = [f"{ip}/{address}" for address in expected_urls]
		message = "\n".join(message)
		
		send_message(message)
		return func(url)
	return decorated_function





def store_to_csv(dict_data):
	with open("7shifts.csv", "a") as outfile:
		writer = csv.writer(outfile)
		writer.writerow(dict_data.values())


def urls_to_string(url=None):
	global ip
	message = [f"{ip}/{x}" for x in expected_urls]
	message = "\n".join(message)
	return message

