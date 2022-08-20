# Using this wrapper on a flask route enables one time use registration urls

# Once a url is requested it gets deleted and a new one generated.

"""
Example Usage:

from flask_single_url import *

# creating urls
add_url(5) # generating 5 urls
add_url(url='a_url_name') # creating named urls


# applying the wrapper
@one_time_url
@app.route('/')
def home():
	return index.html
"""
from string import ascii_lowercase, ascii_uppercase
from random import choices


global expected_urls
expected_urls = []

def one_time_url(func):
	global expected_urls
	@wraps(func)
	def decorated_function(url):
		if url in expected_urls:
			remove_url(url)
			add_url()
		return func(url)
	return decorated_function

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