from flask import Flask, request, render_template, url_for, redirect
from functools import wraps
from random import choices
from string import ascii_lowercase
from telegram_bot import send_message
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase
import json, csv
import socket

global ip
global expected_urls
global telegram_bot_subnet

telegram_bot_subnet = '149.154.161'
ip = 'www.7shifts.online'
expected_urls = []


def add_url(num_urls=1,url=None):
	global expected_urls
	
	for num in range(num_urls):
		if not url:
			numbers=''.join([str(num) for num in range(10)])
			url = ''.join(choices(ascii_lowercase+ascii_uppercase+numbers,k=10))
			url = 'signup/' + url
		expected_urls.append(url)
	return True


def remove_url(url):
	global expected_urls
	if url in expected_urls:
		expected_urls.pop(expected_urls.index(url))
		return True
	else:
		print('error in function < remove_url() >, url not found in expected_urls')
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


def one_time_url(func):
	global expected_urls
	@wraps(func)
	def decorated_function(url):
		if block_ip(request):
			return 'Fuck off'
		url = 'signup/' + url
		match request.method:
			case 'GET':
				if url in expected_urls:
					add_url(url=url+'/submit')
				else:
					return f'INVALID URL'
			case 'POST':
				url = f"{url}/submit"
				if url in expected_urls:
					add_url()
				else:
					return f'INVALID URL'
		
		remove_url(url)
		return func(url)
	return decorated_function


def store_data(dict_data):
	with open("7shifts.csv", "a") as outfile:
		writer = csv.writer(outfile)
		writer.writerow(dict_data.values())


def urls_to_string(url=None):
	global ip
	message = [f"{ip}/{x}" for x in expected_urls]
	message = "\n".join(message)
	return message