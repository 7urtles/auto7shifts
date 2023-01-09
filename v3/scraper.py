import logging
import requests
from datetime import datetime
from tools.shift_tools import convert_shift_date, date_to_weekday
# *******************************************************************************

class ShiftScraper:
	def __init__(self, email:str="charleshparmley@icloud.com", password:str="Earthday19!@22", user_agent=None):
		self.email = email
		self.password = password
		self.user_id = None
		self.days_scheduled = []
		self.session = requests.Session()
		self.session.headers["user-agent"] = user_agent

	def __login(self) -> bool:
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
		logging.error("Login Failed")
		return False

	def __update_user(self) -> str | None:
		logging.info("Updating Account Data")
		user_account_request_data = {
	    	'url':"https://app.7shifts.com/api/v2/company/139871/account"
		}
		self.user_id = self.session.get(**user_account_request_data).json()['data']['user_id']

		logging.debug(f"User ID: {self.user_id}")
		return self.user_id

	def __update_days_scheduled(self) -> None:
		self.days_scheduled = []
		logging.info("Updating Scheduled Days")
		employee_shift_request_data = {
	    	'url':"https://app.7shifts.com/api/v1/schedule/shifts",
			'params' : {
			    'week': f"{datetime.date(datetime.today())}",
			    'location_id': '176547',
			    'department_id': '249830',
			}
		}
		employee_shifts = self.session.get(**employee_shift_request_data).json()['data']

		for shift in employee_shifts:	
			#if the shift belongs to the user
			if shift['user_id'] == self.user_id:
				# Get shifts day of the week
				shift_day = date_to_weekday(convert_shift_date(shift['start'].split(' ')[0]))
				self.days_scheduled.append(shift_day)

	def __update_pool(self) -> list[dict]:
		logging.info("Updating Shift Pool")
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
		logging.debug(f"Shift Pool: {shift_pool}")
		return shift_pool

	def pickup_shift(self, shift_id) -> bool:
		shift = self.shift_pool.shifts[shift_id]
		shift_pool_id = shift.shift_pool_id
		user = shift.user if shift.user else {'firstName': 'HOUSE SHIFT'}
		logging.info(f"Picking up {shift.role['name']} shift from {user['firstName']} with pool id: {shift_pool_id} for user: {self.email}")
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
		# response = self.session.post(**shift_pickup_request_data)
		logging.info('SHIFT CLAIMED')
		return True

	def shift_pool(self) -> bool:
		if self.__login():
			if self.__update_user():
				self.__update_days_scheduled(self)
				return self.__update_pool()
		return False

	def login(self) -> bool:
		"""
		Both self.login() & self.update_account_data() must be run to gain
		necessary cookies and headers.
		"""
		if self.__login():
			if self.__update_user():
				self.__update_days_scheduled()
				self.__update_pool()
				return True
		return False

	def __repr__(self):
		return f"<ShiftScraper: {self.user_id}>"

# *******************************************************************************