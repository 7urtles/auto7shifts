
# -----------------------------------------------------------------------------

class TelegramBot:
	token = '5387420836:AAHHT6b5K7B-L1xZe0T-fwSFHwDDx-Vrv00'
	update_url = f'https://api.telegram.org/bot{token}/getUpdates'

	# Chat id is found in response returned from the update_url
	chat_id = '5379140712'
	message = 'A simple message'

	def send_message(message):
		message_url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
		res = requests.post(message_url)
		return True

# -----------------------------------------------------------------------------