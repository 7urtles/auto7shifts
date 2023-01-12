import logging
import getpass
from scraper import ShiftScraper
from simple_term_menu import TerminalMenu
from pprint import pprint


account = ShiftScraper()
welcome_text = "--Welcome to ezShifts--"
login_text = "Please Login:"
user_preferences = {
	'roles': [],
	'days' : [],
	'locations': [],
}

def main():
	while True:
		if verify_login():
			logging.debug(f"{account.first_name=}")
			main_menu()
		else:
			main_menu()


def main_menu() -> bool:
	selected_options_display = [""] + [f"{title.capitalize()}: {', '.join(choices)}" for title,choices in user_preferences.items()] + [""]
	menu_options = {
		"options" : ["[1] Roles", "[2] Days", "[3] Locations", "[4] Exit"] if account.user_id else ["[1] Email", "[2] Password"],
		"actions" : [get_selections, get_selections, get_selections, exit_program] if account.user_id else [set_username, set_userpass],
		"values" : [account.allowed_roles, [{"name":"Monday"}, {"name":"Tuesday"}, {"name":"Wednesday"}, {"name":"Thursday"}, {"name":"Friday"}, {"name":"Saturday"}, {"name":"Sunday"}], account.allowed_locations, [{"name":None}]]
	}
	logging.debug(list(user_preferences.values()))
	if (account.email and account.password) and not account.user_id:
		menu_options['options'].append(f"[{len(menu_options['options'])+1}] Login")
		menu_options['actions'].append(send_login)

	if all(user_preferences.values()) and (account.email and account.password) and account.user_id:
		menu_options['options'].insert(len(menu_options['options'])-1,f"[{len(menu_options['options'])-1}] Run")
		menu_options['actions'].append(run)

	terminal_menu = TerminalMenu(menu_options['options'], title = selected_options_display)
	menu_entry_index = terminal_menu.show()

	logging.debug(f"{menu_entry_index=}")
	selected_action = menu_options['actions'][menu_entry_index]
	possible_values = menu_options['values'][menu_entry_index]
	selected_category = list(user_preferences.keys())[menu_entry_index]
	selected_action(possible_values, selected_category)
	return True


def get_selections(possible_values:list = None, category = None):
	possible_values = [value['name'] for value in possible_values]
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
	logging.info("RUNNING")

def user_login(user_name:str = None, user_pass:str = None) -> bool:
	if account.user_id:
		return True

	options = ["[1] Email", "[2] Password"]
	actions = [set_username, set_userpass]

	if account.email and account.password:
		options.append(f"[{len(options)+1}] Login")
		actions.append(send_login)

	options.append(f"[{len(options)+1}] Back")
	actions.append(exit_program)

	terminal_menu = TerminalMenu(options)
	pprint(terminal_menu.__dict__)
	menu_entry_index = terminal_menu.show()

	logging.debug(f"{options[menu_entry_index]=}")

	actions[menu_entry_index]()


def send_login(x,y):
	account.login()
	if account.user_id:
		logging.info("User login success")
	else:
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

def set_username(email:str = None):
	account.email = input(": ")
	if account.email:
		logging.info("Email set")
		logging.debug(f"{account.email=}")
		return True
	return False

def set_userpass(password:str = None):
	account.password = getpass.getpass(": ")
	if account.password:
		logging.info("Password set")
		logging.debug(f"{account.password=}")
		return True
	return False


if __name__ == "__main__":
	logging.basicConfig(
		#format='[%(asctime)s][%(levelname)s][%(name)s]%(filename)s[%(lineno)d]:%(funcName)s() -> %(message)s', 
		level=logging.ERROR
		#datefmt='%m/%d/%Y %I:%M:%S %p'
	)
	main()