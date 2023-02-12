import logging
import requests
from datetime import datetime
from tools.shift_tools import shift_to_datetime, date_to_weekday
from dataclasses import dataclass
from pprint import pprint
# *******************************************************************************

''' 
The ShiftScrapers functions for the majority follow this pattern:
	1. Construct request
	2. Send request
	3. React to response
	
Their purpose is to be called in groups to perform a larger task such as performing login
and updating user data.

The exception to this is ShiftScraper.pickup_shift() because of always updating user data before calling it.
'''
@dataclass
class Employee:
    id: str
    firstname: str
    lastname: str
    birth_date: str
    email: str
    photo: str
    mobile_phone: str
    employee_id: str
    notes: str
    address: str
    appear_as_employee: str
    active: str
    company_id: str

    def dict(self) -> dict:
        return vars(self)

    def __repr__(self) -> str:
        return f'<Employee id:{self.id}>'


class SessionInstance:
	def __init__(self, email:str = None, password:str = None, user_agent = None):
		self.email = email
		self.password = password
		self.user_id = ""
		self.first_name = ""
		self.last_name = ""
		self.shifts = []
		self.compaines = []
		self.locations = []
		self.roles = []
		self.days_scheduled = []
		self.employee_data = {}
		self.session = requests.Session()
		self.session.headers["user-agent"] = user_agent

	def _login(self) -> bool:
		"""
		Stores login cookies to a requests.session
		This classes other functions rely on these cookies to operate
		"""
		login_request_data = {
		    'url':'https://app.7shifts.com/users/login',
		    'data':{
		        '_method': 'POST',
		        'data[User][email]': self.email,
		        'data[User][password]': self.password,
		        'data[User][keep_me_logged_in]': [
		            '0',
		            '1',
		        ],
		    },
		    'allow_redirects':False
		}
		response = self.session.post(**login_request_data)
		if response.status_code == 302:
			logging.info("Loggin Success")
			return True
		logging.error("Login Failure")
		raise ValueError("Invalid email or password")
		return False

	def _read_user_info(self) -> dict:
		"""
		Requests user account info from 7shifts.com
		"""
		logging.info("Updating Account Data")
		user_account_request_data = {
	    	'url':"https://app.7shifts.com/api/v2/company/254692/account"
		}
		try:
			account_data = self.session.get(**user_account_request_data).json()['data']
		except ValueError:
			logging.debug("Fetching user details failed. Data not found.")
			return False
		return account_data

	def	_update_session_info(self, account_data) -> bool:
		"""
		Takes in user data requested from 7shifts.com, storing it in the classes
		instance variables.
		"""
		self.user_id = account_data['user_id']
		self.first_name = account_data['first_name']
		self.last_name = account_data['last_name']
		self.compaines = account_data['company']
		self.locations = {location['id']:location for location in account_data['locations']}
		self.roles = {role['id']:role for role in account_data['roles']}
		logging.debug(f"Updataing Session Info")
		logging.debug(f"{self.user_id=}\n{self.email=}")
		return True

	def _read_user_schedule(self) -> None:
		"""
		Requests the days a use is scheduled to work from 7shifts.com
		"""
		self.days_scheduled = []
		logging.info("Updating Scheduled Days")
		employee_shift_request_data = {
	    	'url':"https://app.7shifts.com/api/v1/schedule/shifts",
			'params' : {
			    'week': f"{datetime.date(datetime.today())}",
			    'location_id': '319579',
			    'department_id': '464752',
			}
		}
		try:
			employee_shifts = self.session.get(**employee_shift_request_data).json()['data']
			return employee_shifts
		except ValueError:
			logging.debug("Fetching user schedule failed. Data not found.")
		

	def _update_session_schedule(self, employee_shifts):
		"""
		Takes in user schedule data requested from 7shifts.com, storing it in the classes
		instance variables.
		"""
		for shift in employee_shifts:	
			#if the shift belongs to the user
			if shift['user_id'] == self.user_id:
				# Get shifts day of the week
				self.shifts.append(shift)
				shift_day = date_to_weekday(shift_to_datetime(shift['start'].split(' ')[0]))
				self.days_scheduled.append(shift_day)
		logging.debug(f"Updating Session Schedule")
		logging.debug(f"Currently Scheduled: {self.days_scheduled}")
		return True


	def _read_user_pool(self) -> list[dict]:
		"""
		Requests shifts claimable by the user from 7shifts.com
		"""
		logging.info("Updating Shift Pool")
		shift_offers_request_data = {
		    'url':"https://app.7shifts.com/gql",
		    'json':{
		        'operationName': 'GetLegacyShiftPoolOffers',
		        'variables': {
		            'companyId': '254692',
		            'cursor': None,
		            'limit': 20,
		        },
		        'query': 'query GetLegacyShiftPoolOffers($companyId: ID!, $cursor: String, $limit: Int) {\n  getShiftPool(companyId: $companyId, cursor: $cursor, limit: $limit) {\n    legacyShiftPoolOffers {\n      ...LegacyShiftPoolOfferFragment\n      _typename\n    }\n    cursor {\n      prev\n      next\n      count\n      _typename\n    }\n    _typename\n  }\n}\n\nfragment LegacyShiftPoolOfferFragment on LegacyShiftPoolOffer {\n  shiftPool {\n    id\n    offerType\n    offerId\n    offers {\n      id\n      firstname\n      lastname\n      photo\n      _typename\n    }\n    _typename\n  }\n  comments\n  shift {\n    id\n    start\n    end\n    open\n    user {\n      userId\n      firstName\n      lastName\n      photo\n      _typename\n    }\n    locationId\n    location {\n      address\n      timezone\n      _typename\n    }\n    department {\n      name\n      _typename\n    }\n    role {\n      id\n      name\n      color\n      _typename\n    }\n    _typename\n  }\n  location {\n    address\n    timezone\n    _typename\n  }\n  bids {\n    id\n    userId\n    _typename\n  }\n  _typename\n}\n',
		    },
		    'allow_redirects':False
		}
		try:
			shift_pool = self.session.post(**shift_offers_request_data).json()
			return shift_pool
		except ValueError:
			logging.debug("Fetching user schedule failed. Data not found.")
		
	def _update_session_pool(self, shift_pool:dict) -> bool:
		logging.debug(f"Shift Pool: {shift_pool}")
		if shift_pool.get('data'):
			shift_pool = shift_pool['data']['getShiftPool']['legacyShiftPoolOffers']
		return True

	def pickup_shift(self, shift) -> bool:
		"""
		Sends a post request to 7shifts.com in order to claim a shift for the user
		"""
		user = shift.user if shift.user else {'firstName': 'HOUSE SHIFT'}
		logging.info(f"Picking up {shift.role['name']} shift from {user['firstName']} with pool id: {shift_pool_id} for user: {self.email}")
		shift_pickup_request_data = {
			'url': 'https://app.7shifts.com/gql',
			'json': {
				'operationName': 'BidOnShiftPool',
				'variables': {
					'input': {
						'shiftPoolId': shift.shift_pool_id,
						'userId': self.user_id,
					},
				},
				'query': 'mutation BidOnShiftPool($input: BidOnShiftPoolInput!) {\n  bidOnShiftPool(bidOnShiftPoolInput: $input)\n}\n',
			},
			'allow_redirects':False
		}
		response = self.session.post(**shift_pickup_request_data)
		logging.info('SHIFT CLAIMED')
		return True

	def update_employee_data(self) -> list[dict]:
		"""
		Request user data of all employee profiles accessable to the user
		"""
		employees_request_data = {
			'url':'https://app.7shifts.com/api/v1/users',
			'params':{
			    'deep': '1',
			    'offset': '0',
			    'active': '0', # '1' for current employees, or '0' for past employees
			}
		}
		# Getting all active employees
		try:
			employee_data = self.session.get(**employees_request_data).json()['data']
			employees_request_data['params']['active'] = '1'
			employee_data += self.session.get(**employees_request_data).json()['data']
		except ValueError:
			logging.debug(employee_data)
			logging.debug("Fetching company employee data failed. Data not found.")

		# Update known employees with newly found data
		self.employee_data.update(
			{
				employee['user']['id']:
					{
						"firstname" : employee['user']['firstname'],
						"lastname" : employee['user']['lastname'],
						"birth_date" : employee['user']['birth_date'],
						"email" : employee['user']['email'],
						"photo" : employee['user']['photo'],
						"mobile_phone" : employee['user']['mobile_phone'],
						"employee_id" : employee['user']['employee_id'],
						"notes" : employee['user']['notes'],
						"address" : employee['user']['address'],
						"appear_as_employee" : employee['user']['appear_as_employee'],
						"active" : employee['user']['active'],
						"company_id" : employee['user']['company_id']
					}
				for employee in employee_data
			}
		)
		"""
		# Changing query to target inactive employees
		employees_request_data['params']['active'] = 0
		# Getting and inserting inactive employees 
		self.employee_data.update(self.session.get(**employees_request_data).json()['data'])
		"""
		return self.employee_data


	def update(self) -> bool:
		"""
		Refreshes the instance variables data
		"""
		# Gather cookies needed for account based functions to run
		self._login()

		# Read user account info from 7shifts
		user_info = self._read_user_info()
		# Store user account info to session
		self._update_session_info(user_info)

		# Read user work schedule from 7shifts
		schedule = self._read_user_schedule()
		# Store user work schedule to session
		self._update_session_schedule(schedule)

		# Read user shift pool from 7shifts
		user_pool = self._read_user_pool()
		# Store user shift pool to session
		self._update_session_pool(user_pool)

		return True


	def _repr_(self):
		return f"<ShiftScraper: {self.user_id}>"



# *******************************************************************************
