
import time
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


		self.shift_wanted = {
			'position':'Security',
			'day':'Sun',
			'time':'4:00PM-11:00PM'
		}

		self.shift_taken = False
		self.telegram_bot_message = ""
		self.debug = True
		self.driver = self.setup_webdriver()
		

	#-----------------------------------------------------------------

	def setup_webdriver(self):
		"""
		Prepping web driver & loading login cookies
		"""
		# Initializing driver options
		fireFoxOptions = selenium.webdriver.FirefoxOptions()
		if self.debug:
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
	def save_cookies(self):
		self.driver.get("https://app.7shifts.com/users/login?redirect=/company/139871/shift_pool/up_for_grabs")
		time.sleep(35)
		pickle.dump(self.driver.get_cookies() , open("cookies.pkl","wb"))

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
		if self.shift_wanted['position'].lower() in shift.text.lower():
			shift_columns = shift.find_elements(By.CSS_SELECTOR, self.shift_details_selector);
			for column in shift_columns[:-3]:
				
				if column.text[:3] == self.shift_wanted['day']:

					return column

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
			# REPLACE THIS LINE WITH .click() EVENT ON THE PICKUP BUTTON WHEN READY TO TAKE SHIFTS
			"""*****************************************************"""
			return True
		except:
			print('Shift pickup failed!')
			return False

	#-----------------------------------------------------------------
	def check_available_times(self,shift_data):
			
		shift_data = shift_data.text.strip().split(' ')

		shift_times = [data for data in shift_data if ":" in data]

		shift_time = '-'.join(shift_times)

		if shift_time == self.shift_wanted['time']:
			return True


	def run(self):
		"""
		Bots driver code.
			-load 7shifts shift pool
			-checks available shifts
			-verify available shift position and time
			-pick up shift
			-send user new shift info via telegram
		"""
		print(f"Searching available {self.shift_wanted['position']} shifts for: {self.shift_wanted['day']}")

		# Open the page showing available shifts
		self.driver.get(self.SHIFT_POOL_URL)

		# Process page elements into a list of found shifts
		shifts = list(self.get_shift_table())

		# Restart the loop if no shifts are up for grabs
		if not len(shifts):
			return False
		# Look at all found shifts
		for shift in shifts:
			# Match a shift to the users requested day
			shift_data = self.check_available_days(shift)
			#If a shift is on that day
			if shift_data:
				# Check if the shifts time matches the users requested time
				if self.check_available_times(shift_data):
					# If the bot clicks the shift pickup button
					if self.pickup_shift(shift):
						print('Shift Picked Up:')
						# Set message with found shifts information
						self.telegram_bot_message = "\t"+shift_data.text+"\n"
						return True
		else:
			return False

	#-----------------------------------------------------------------

#*************************************

# Main Driver Code
if __name__ == '__main__':
	# Initialize new scraper instance
	scraper = Shift_Grabber()

	# Will continue to check for open shifts until all desired shifts are grabbed.
	while not scraper.shift_taken:
		# scraper.save_cookies()

		# If the scraper picks up a shift
		if scraper.run():
			print(scraper.telegram_bot_message)
			# Send shift details to users telegram account
			telegram_bot.send_message('Shift picked up, check your schedule!'+'\n'+scraper.telegram_bot_message)
			# Break the loop
			scraper.shift_taken = True
	# Close the headless browser and ending session
	scraper.driver.close()