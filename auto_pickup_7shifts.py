

import pickle
import selenium.webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import telegram_bot

#*************************************

class Shift_Grabber:
	def __init__(self):
		self.SHIFT_POOL_URL = "https://app.7shifts.com/company/139871/shift_pool/up_for_grabs"
		self.shift_table_selector = "._1d8Ci"
		self.shift_details_selector = "._OTcMc"
		self.shift_pickup_button = 'button'
		self.confirm_pickup_button = '/html/body/div[12]/div/div/div/div[3]/div/button[1]'
		self.days_wanted = ['Fri', 'Sat']
		self.position_title = 'security'
		self.telegram_bot_message = ""
		self.driver = self.setup_webdriver()

	#-----------------------------------------------------------------

	def setup_webdriver(self):
		"""
		Prepping web driver & loading login cookies
		"""
		# Initializing driver options
		fireFoxOptions = selenium.webdriver.FirefoxOptions()

		# Prevent showing browser window
		fireFoxOptions.add_argument('--headless')

		# Create webdriver and add specified runtime arguments
		driver = selenium.webdriver.Firefox(options=fireFoxOptions)

		# Pre-load 7shifts url in order to add cookies (url must match cookie url)
		driver.get(self.SHIFT_POOL_URL)

		# Load login cookies
		cookies = pickle.load(open("cookies.pkl", "rb"))

		# Add each cookie to the current driver 
		for cookie in cookies:
		    driver.add_cookie(cookie)

		return driver

	#-----------------------------------------------------------------

	def get_shift_table(self):
		"""
		Attempting to retrieve html table containing individual shift entries
		"""
		delay = 3 # seconds

		try:
		    WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "._1d8Ci")))
		    table = self.driver.find_elements(By.CSS_SELECTOR, self.shift_table_selector);
		    return table
		except:
		    return False

	#-----------------------------------------------------------------

	def check_available_days(self,shift):
		"""
		Checking for open shifts and available dates for the specified position type
		"""
		if self.position_title in shift.text.lower():
			shift_columns = shift.find_elements(By.CSS_SELECTOR, self.shift_details_selector);
			
			for column in shift_columns[:-3]:
				
				if column.text[:3] in self.days_wanted:
					print('Shift Found:')
					self.telegram_bot_message = "\t"+column.text+"\n"
					print(self.telegram_bot_message)
					self.days_wanted.pop(self.days_wanted.index(column.text[:3]))
					return True

	#-----------------------------------------------------------------

	def pickup_shift(self,shift):
		"""
		Attempts to find the first available shift for specified position type and day
		"""
		try:
			OPEN_SHIFT = shift.find_element(By.TAG_NAME, self.shift_pickup_button)
			OPEN_SHIFT.send_keys(Keys.RETURN)
			"""DONT SEND A CLICK UNLESS SHIFT PICKUP IS INTENDED!!!!"""
			pickup_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[11]/div/div/div/div[3]/div/button[1]')))
			# REPLACE THIS LINE WITH .click() WHEN READY TO TAKE SHIFTS
			"""*****************************************************"""
			return True
		except:
			print('Shift pickup failed!')
			return False

	#-----------------------------------------------------------------
	
	def run(self):
		"""
		Bots driver code.
			-loads page
			-checks available shifts
			-verifies available shift positions and times
			-picks up the shift
		"""
		print(f"Searching available {self.position_title} shifts for: {self.days_wanted}")

		self.driver.get(self.SHIFT_POOL_URL)

		shifts = list(self.get_shift_table())

		if not len(shifts):
			return False

		for shift in shifts:
			if self.check_available_days(shift):
				if self.pickup_shift(shift):
					return True

		return False

	#-----------------------------------------------------------------

#*************************************

# Main Driver Code
if __name__ == '__main__':
	# Initialize new scraper instance
	scraper = Shift_Grabber()

	# Will continue to check for open shifts until all desired shifts are grabbed.
	while scraper.days_wanted:
		shift_picked_up = scraper.run()

		# Send employee a telegram message for every successfully picked up shift
		# Message contains shift date/time details
		if shift_picked_up:
			telegram_bot.send_message('Shift picked up, check your schedule!'+'\n'+scraper.telegram_bot_message)

	scraper.driver.close()