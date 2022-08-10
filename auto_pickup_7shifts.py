import os
import time
import pickle

import selenium.webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dotenv import load_dotenv
from pprint import pprint

from tools import twilio_sms

#*************************************

class Shift_Grabber:
	def __init__(self, shift_pool_url, CONFIRM_PICKUP_BUTTON):
		self.shift_pool_url = shift_pool_url
		self.shift_table_selector = "._1d8Ci"
		self.shift_details_selector = "._OTcMc"
		self.shift_pickup_button = 'button'
		self.CONFIRM_PICKUP_BUTTON = CONFIRM_PICKUP_BUTTON
		self.shift_wanted = {
			'location':'Yard Bar Westport',
			'position':'Security',
			'day':'Sun',
			'time':['4:00PM','11:00PM']
		}
		self.shift_taken = False
		self.headless = True
		self.driver = None
		self.first_run = True
		self.setup_webdriver()

	#-----------------------------------------------------------------

	def setup_webdriver(self):
		"""
		Prepping web driver & loading login cookies
		"""
		# Initializing driver options
		fireFoxOptions = selenium.webdriver.FirefoxOptions()
		if self.headless:
			# Prevent showing browser window
			fireFoxOptions.add_argument('--headless')

		# Create webdriver and add specified runtime arguments
		self.driver = selenium.webdriver.Firefox(options=fireFoxOptions)
		return True
	#-----------------------------------------------------------------

	def save_cookies(self) -> bool:
		self.driver.get(self.shift_pool_url)
		time.sleep(60)
		pickle.dump(self.driver.get_cookies() , open("cookies/cookies.pkl","wb"))
		return True


	def add_cookies(self) -> bool:
		# Pre-load 7shifts url in order to add cookies (url must match cookie url)
		self.driver.get(self.shift_pool_url)

		# Load login cookies
		cookies = pickle.load(open("cookies/cookies.pkl", "rb"))

		# Add each cookie to the current driver
		try:
			for cookie in cookies:
				self.driver.add_cookie(cookie)
				True
		except:
			print('Adding cookie failed: Web address and cookie address must match')
			return False

	#-----------------------------------------------------------------

	def get_shift_table(self) -> list | bool:
		"""
		Attempting to retrieve html table containing individual shift entries
		"""
		delay = 3 # seconds

		try:
		    WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "._1d8Ci")))
		    table = self.driver.find_elements(By.CSS_SELECTOR, self.shift_table_selector);
		    return list(table)
		except:
			print(table)
			return False

	#-----------------------------------------------------------------

	def parse_shift(self, shift:list) -> dict:
		# Labels to be used in attribute dictionaries
		detail_labels = ['shift_poster','position', 'date', 'location', 'shift_type', 'position', 'button_label']
		date_labels = ['day_week', 'month', 'day_month', 'year', 'clock_in', 'clock_out']

		# Select all of the html text elements within the shift html table
		shift_details = shift.find_elements(By.CSS_SELECTOR, self.shift_details_selector)

		# Create dict of labels and shift attributes
		shift_details = {detail_labels[i]:shift_details[i].text for i in range(len(detail_labels))}

		# Format shifts time
		shift_details['date'] = shift_details['date'].replace(',','').replace(' -','').split(' ')

		# Convert shifts date details into a dict of accessable date traits
		shift_details['date'] = dict(zip(date_labels, shift_details['date']))
		return shift_details

	#-----------------------------------------------------------------

	def pickup_shift(self, shift:list) -> dict:
		"""
		Attempts to find the first available shift for specified position type and day
		"""
		try:
			open_shift = shift.find_element(By.TAG_NAME, self.shift_pickup_button)
			open_shift.send_keys(Keys.RETURN)
			"""DONT SEND A CLICK UNLESS SHIFT PICKUP IS INTENDED!!!!"""
			# pickup_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, self.CONFIRM_PICKUP_BUTTON)))
			# pickup_button.send_keys(Keys.RETURN)
			# UNCOMMENT ABOVE LINE WHEN READY TO TAKE SHIFTS
			"""*****************************************************"""
			return True
		except:
			print('Shift pickup failed!')
			return False

	#-----------------------------------------------------------------

	def check_shift_location(self, shift_details:dict) -> bool:
		if shift_details['location'] == self.shift_wanted['location']:
			return True

	def check_shift_day(self, shift_details:dict) -> bool:
		"""
		Checking for open shifts and available dates for the specified position type
		"""
		if shift_details['date']['day_week'] == self.shift_wanted['day']:
			return True


	def check_shift_time(self, shift_details:dict) -> bool:
		shift_time = [
			shift_details['date']['clock_in'],
			shift_details['date']['clock_out']
		]
		if shift_time == self.shift_wanted['time']:
			return True

	#-----------------------------------------------------------------

	def stop_webdriver(self) -> bool:
		try:
			self.driver.close()
			return True
		except:
			print("Closing webdriver failed. Webdriver already closed.")
			return False

	#-----------------------------------------------------------------

	def run(self) -> bool:
		"""
		Bots driver code.
			-load 7shifts shift pool
			-checks available shifts
			-verify available shift position and time
			-pick up shift
			-send user new shift info via telegram
		"""
		print(f"Searching available {self.shift_wanted['position'].upper()} shifts for: {self.shift_wanted['day'].upper()}")

		# Direct webdriver to available shifts url
		self.driver.get(self.shift_pool_url)

		if self.first_run == True:
			# Now that the webdrivers current url and the cookies url match the cookies may be added
			self.add_cookies()
			# Reload page with added cookies
			self.driver.get(self.shift_pool_url)
			self.first_run = False

		# Process page elements into a list of found shifts
		try:
			found_shifts = self.get_shift_table()
		except:
			# Restart the loop if no shifts are up for grabs
			print('Shift Pool Empty')
			return False

		# Look at all found shifts
		for shift in found_shifts:
			shift_details = self.parse_shift(shift)
			requested_location_found = self.check_shift_location(shift_details)

			# If the shift day matches the requested day
			if requested_location_found:
				requested_day_found = self.check_shift_day(shift_details)

				# If the shift day matches the requested day
				if requested_day_found:
					requested_time_found = self.check_shift_time(shift_details)

					# If the shift time matches the requested time
					if requested_time_found:

						# If the bot successfully clicks the shift pickup button
						if self.pickup_shift(shift):
							print('Shift Picked Up:')
							pprint(shift_details)
							return True
		else:
			return False
	#-----------------------------------------------------------------

#*************************************

# Main Driver Code
if __name__ == '__main__':
	# Load environment variables
	load_dotenv()

	shift_pool_url = os.getenv('SHIFT_POOL_URL')
	CONFIRM_PICKUP_BUTTON = os.getenv('CONFIRM_PICKUP_BUTTON')

	# Initialize scraper instance
	scraper = Shift_Grabber(shift_pool_url=shift_pool_url, CONFIRM_PICKUP_BUTTON=CONFIRM_PICKUP_BUTTON)

	# if scraper.save_cookies():
	# 	print('login cookies saved')
	# 	exit()

	# Continues to scrape for the requested shift until it's picked up
	while not scraper.shift_taken:
		scraper.shift_taken = scraper.run()

	# # If the scraper picks up a shift send sms notification to user
	# twilio_sms.send_sms()

	# Close the headless browser and ending session
	scraper.stop_webdriver()