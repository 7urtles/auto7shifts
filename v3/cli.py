import logging
import getpass
from scraper import ShiftScraper
from simple_term_menu import TerminalMenu
from pprint import pprint
from tools import shift_tools
import server

account = ShiftScraper()
account.user_agent = server.USER_AGENT
welcome_text = "--Welcome to ezShifts--"
login_text = "Please Login:"
user_preferences = {
	'roles': None,
	'days' : None,
	'locations': None,
}
weekdays = "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
last_index = {"index":0}
def main():
	while True:
		if verify_login():
			logging.debug(f"{account.first_name=}")
			preferences_menu()
		else:
			main_menu()

def main_menu():
	options = ["Login", "Exit"]
	actions = [login_menu, exit_program]


	terminal_menu = TerminalMenu(options, cursor_index=last_index['index'], clear_screen=True)
	menu_entry_index = terminal_menu.show()

	logging.debug(f"{options[menu_entry_index]=}")

	actions[menu_entry_index]()
	return True

def preferences_menu() -> bool:
	welcome_text = f"\nWelcome {account.email},\n\nCurrent Schedule:\n"
	current_shifts = [f"{account.allowed_roles[shift['role_id']]['name']} | {shift_tools.date_to_weekday(shift_tools.convert_shift_date(shift['start'].split(' ')[0]))} | {account.allowed_locations[shift['location_id']]['name']}" for shift in account.user_shifts]
	title = f"\n{welcome_text} {current_shifts}\n"
	menu_options = {
		"options" : [f"Roles: {user_preferences['roles']}", f"Days: {user_preferences['days']}", f"Locations: {user_preferences['locations']}"],
		"actions" : [get_selections for option in user_preferences],
		"values" : [account.allowed_roles, {day:{"name":day} for day in weekdays}, account.allowed_locations]
	}

	logging.debug(list(user_preferences.values()))

	if all(user_preferences.values()) and account.user_id:
		menu_options['options'].append("Run")
		menu_options['actions'].append(run)
		menu_options['values'].append('run')

	menu_options['options'].append("Logout")
	menu_options['actions'].append(exit_program)
	menu_options['values'].append('logout')

	terminal_menu = TerminalMenu(menu_options['options'], title=title, cursor_index=last_index['index'], clear_screen=True)
	
	menu_entry_index = terminal_menu.show()
	logging.debug(f"{terminal_menu.chosen_menu_index=}")
	last_index['index'] = terminal_menu.chosen_menu_index

	selected_action = menu_options['actions'][menu_entry_index]
	possible_values = menu_options['values'][menu_entry_index]
	if possible_values == 'run':
		selected_action()

	selected_category = list(user_preferences.keys())[menu_entry_index]
	selected_action([possible_values, selected_category])
	return True


def get_selections(*args):
	possible_values, category = args[0]
	possible_values = [value['name'] for value in possible_values.values()]
	logging.debug(f"{possible_values=}")

	selection_menu = TerminalMenu(
		possible_values,
		multi_select=True,
		show_multi_select_hint=False,
		clear_menu_on_exit=False,
		preselected_entries=user_preferences[category],
		multi_select_select_on_accept=False,
	)

	logging.debug(f"{user_preferences[category]=}")
	menu_entry_indices = selection_menu.show()
	
	user_preferences[category] = [possible_values[selection] for selection in menu_entry_indices]
	logging.debug(f"{user_preferences=}")
	return True

def run():
	server.app.scraper = account
	server.init_db()
	logging.basicConfig(
		format='[%(asctime)s][%(levelname)s][%(name)s]%(filename)s[%(lineno)d]:%(funcName)s() -> %(message)s', 
		filename='logs/7shifts.log', encoding='utf-8', level=logging.DEBUG, 
		datefmt='%m/%d/%Y %I:%M:%S %p'
	)
	# Launching the callback webserver
	server.app.run(host="0.0.0.0", port=5007)

def login_menu(user_name:str = None, user_pass:str = None) -> bool:
	if account.user_id:
		return True

	options = ["Email", "Password"]
	actions = [set_username, set_userpass]

	if account.email and account.password:
		options.append("Submit")
		actions.append(send_login)

	options.append("Back")
	actions.append(exit_program)

	terminal_menu = TerminalMenu(options, cursor_index=last_index['index'])

	menu_entry_index = terminal_menu.show()
	logging.debug(f"{options[menu_entry_index]=}")
	actions[menu_entry_index]()


def send_login(*args):
	account.login()
	if not account.user_id:
		raise ValueError("Login Failed! Credentials not valid")
		logging.debug(f"{account.user_id=}")
	return True


def verify_login():
	if not account.user_id:
		logging.info("User not logged in")
		return False
	logging.debug(f"{account.user_id=}")
	return True

def exit_program(status = None):
	logging.info("exiting....")
	return False

def set_username(*args):
	account.email = input(": ")
	if account.email:
		logging.info("Email set")
		logging.debug(f"{account.email=}")
		return True
	return False

def set_userpass(*args):
	account.password = getpass.getpass(": ")
	if account.password:
		logging.info("Password set")
		logging.debug(f"{account.password=}")
		return True
	return False


if __name__ == "__main__":
	logging.basicConfig(
		#format='[%(asctime)s][%(levelname)s][%(name)s]%(filename)s[%(lineno)d]:%(funcName)s() -> %(message)s', 
		level=logging.DEBUG
		#datefmt='%m/%d/%Y %I:%M:%S %p'
	)
	main()