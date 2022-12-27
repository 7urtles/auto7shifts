import sys
import requests
from datetime import datetime
from dataclasses import dataclass
sys.path.append("/Users/charles/Github/Auto7shifts/") 
from tools.shifts import *
# *******************************************************************************

class DataCollector:
	def __init__(self, email:str, password:str, user_agent=None):
		self.user_id = None
		self.email = email
		self.password = password
		self.login_success = False
		self.user_data = None
		self.user_shifts = {}
		self.employee_shifts = {}
		self.employee_data = {}
		self.location_data = None
		self.shift_pool = None
		self.session = requests.Session()
		self.session.headers["user-agent"] = user_agent

	def login(self) -> bool:
		login_request_data = {
		    'url':'https://app.7shifts.com/users/login',
		    'data':{
		        '_method': 'POST',
		        'data[_Token][key]': 'cbd332b64ee4f15a967a692a4a237f3a',
		        'data[User][email]': self.email,
		        'data[User][password]': self.password,
		        'data[User][redirect]': '',
		        'data[User][keep_me_logged_in]': [
		            '0',
		            '1',
		        ],
		        'data[_Token][fields]': 'be4fd85121b5dd0aea168db08ad7a5daf34c830b%3AUser.redirect',
		        'data[_Token][unlocked]': '',
		    },
		    'allow_redirects':False
		}
		response = self.session.post(**login_request_data)
		return True

	def update_account_data(self) -> list:
		user_account_request_data = {
	    	'url':"https://app.7shifts.com/api/v2/company/139871/account"
		}
		self.user_data = self.session.get(**user_account_request_data).json()['data']
		self.user_id = self.user_data['user_id']
		return self.user_data

	def update_employee_shifts(self) -> list[dict]:
		employee_shift_request_data = {
	    	'url':"https://app.7shifts.com/api/v1/schedule/shifts",

			'params' : {
			    'week': '2022-12-26',
			    'location_id': '176547',
			    'department_id': '249830',
			}
		}
		employee_shifts = self.session.get(**employee_shift_request_data).json()['data']

		for shift in employee_shifts:
			shift = UserShift(**shift)
			shift.start = datetime.strptime(shift.start, '%Y-%m-%d %H:%M:%S')
			#if the shift belongs to the user
			if shift.user_id == self.user_id:
				# add it to the user shifts
				self.user_shifts[shift.id] = shift
			# if the shift id hasn't been found yet
			if shift.id not in self.employee_shifts:
				# store it and the shift into known employee shifts
				self.employee_shifts[shift.id] = shift
		return self.employee_shifts
	
	def update_employee_data(self) -> list[dict]:
		employees_request_data = {
			'url':'https://app.7shifts.com/api/v1/users',
			'params':{
			    'deep': '1',
			    'offset': '0',
			    'active': '1', # '1' for current employees, or '0' for past employees
			}
		}
		# Getting all active employees
		employee_data = self.session.get(**employees_request_data).json()['data']
		# Update known employees with newly found data
		self.employee_data.update({employee['user']['id']:Employee(**employee['user']) for employee in employee_data})
		"""
		# Changing query to target inactive employees
		employees_request_data['params']['active'] = 0
		# Getting and inserting inactive employees 
		self.employee_data.update(self.session.get(**employees_request_data).json()['data'])
		"""
		return self.employee_data

	def update_location_data(self) -> list[dict]:
		user_locations_request_data = {
	    	'url':f"https://app.7shifts.com/api/v2/company/139871/users/{self.user_id}/authorized_locations"
		}
		self.user_locations = self.session.get(**user_locations_request_data).json()['data']
		return self.user_locations

	def update_shift_pool(self) -> list[dict]:
		shift_offers_request_data = {
		    'url':"https://app.7shifts.com/gql",
		    'json':{
		        'operationName': 'GetLegacyShiftPoolOffers',
		        'variables': {
		            'companyId': '139871',
		            'cursor': None,
		            'limit': 20,
		        },
		        'query': 'query GetLegacyShiftPoolOffers($companyId: ID!, $cursor: String, $limit: Int) {\n  getShiftPool(companyId: $companyId, cursor: $cursor, limit: $limit) {\n    legacyShiftPoolOffers {\n      ...LegacyShiftPoolOfferFragment\n      __typename\n    }\n    cursor {\n      prev\n      next\n      count\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment LegacyShiftPoolOfferFragment on LegacyShiftPoolOffer {\n  shiftPool {\n    id\n    offerType\n    offerId\n    offers {\n      id\n      firstname\n      lastname\n      photo\n      __typename\n    }\n    __typename\n  }\n  comments\n  shift {\n    id\n    start\n    end\n    open\n    user {\n      userId\n      firstName\n      lastName\n      photo\n      __typename\n    }\n    locationId\n    location {\n      address\n      timezone\n      __typename\n    }\n    department {\n      name\n      __typename\n    }\n    role {\n      id\n      name\n      color\n      __typename\n    }\n    __typename\n  }\n  location {\n    address\n    timezone\n    __typename\n  }\n  bids {\n    id\n    userId\n    __typename\n  }\n  __typename\n}\n',
		    },
		    'allow_redirects':False
		}
		shift_pool = self.session.post(**shift_offers_request_data).json()['data']['getShiftPool']['legacyShiftPoolOffers']
		
		if not self.shift_pool:
			self.shift_pool = ShiftPool(shift_pool)
		else:
			self.shift_pool.update_pool(shift_pool)
		return self.shift_pool

	def pickup_shift(self, shift_id) -> bool:
		shift = self.shift_pool.shifts[shift_id]
		shift_pool_id = shift.shift_pool_id
		user = shift.user if shift.user else {'firstName': 'HOUSE SHIFT'}
		print(f"Picking up {shift.role['name']} shift from {user['firstName']} with pool id: {shift_pool_id} for user: {self.email}")
		shift_pickup_request_data = {
			'url': 'https://app.7shifts.com/gql',
			'json': {
				'operationName': 'BidOnShiftPool',
				'variables': {
					'input': {
						'shiftPoolId': shift_pool_id,
						'userId': self.user_id,
					},
				},
				'query': 'mutation BidOnShiftPool($input: BidOnShiftPoolInput!) {\n  bidOnShiftPool(bidOnShiftPoolInput: $input)\n}\n',
			},
			'allow_redirects':False
		}
		response = self.session.post(**shift_pickup_request_data)
		return True

	def run(self) -> bool:
		"""
		Both self.login() & self.update_account_data() must be run to gain
		necessary cookies and headers for the rest of the classes functions
		to run successfully.
		"""
		self.login()
		self.update_account_data()
		# The below calls can run in parallell if need be to reduce time spent collecting data.
		# self.update_employee_shifts()
		# self.update_employee_data()
		# self.update_location_data()
		# self.update_shift_pool()
		return True

	def __repr__(self):
		return f"<DataCollector: {self.user_id}>"

# *******************************************************************************