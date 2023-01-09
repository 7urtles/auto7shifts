# -----------------------------------------------------------------------------
import requests
class TelegramBot:
	def __init__(self):
		self.token = '5387420836:AAHHT6b5K7B-L1xZe0T-fwSFHwDDx-Vrv00'
		self.update_url = f'https://api.telegram.org/bot{self.token}/getUpdates'

		# Chat id is found in response returned from the update_url
		self.chat_id = '5379140712'
		self.message = 'A simple message'

	def send_message(self):
		message_url = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={self.message}'
		res = requests.post(message_url)
		return True

# -----------------------------------------------------------------------------

bot = TelegramBot()
bot.send_message()
