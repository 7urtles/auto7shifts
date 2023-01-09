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
class SingleURL:
	def __init__(self):
		self.urls = []

	def one_time_url(self, func):
		@wraps(func)
		def decorated_function(url):
			if url in self.urls:
				remove_url(url)
				add_url()
			return func(url)
		return decorated_function

	def add_url(self, num_urls=1, url=None):
		for num in range(num_urls):
			if not url:
				numbers=''.join([str(num) for num in range(10)])
				url = ''.join(choices(ascii_lowercase+ascii_uppercase+numbers,k=10))
				url = 'signup/' + url
			self.urls.append(url)
		return True

	def remove_url(self, url):
		if url not in self.urls:
			print('error in function < remove_url() >, url not found in urls')
			return False

		self.urls.pop(self.urls.index(url))
		return True