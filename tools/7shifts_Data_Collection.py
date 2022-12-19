


import requests
import json




class DataCollector:
	def __init__(self, email:str, password:str):
		self.user_id = None
		self.email = email
		self.password = password
		self.login_success = False
		self.account_data = None
		self.company_users = None
		self.work_locations = None
		self.shift_pool = None
		self.session = requests.Session()

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
		response_code = self.session.post(**login_request_data).status_code
		if response_code != 302:
			raise ValueError(f"[error]: Invalid stats code.\tExpected 302, got {response_code}")

		return True

	def load_account_data(self) -> str:
		user_account_request_data = {
	    	'url':"https://app.7shifts.com/api/v2/company/139871/account"
		}
		account_data_json = self.session.get(**user_account_request_data).json()
		self.user_id = account_data_json['data']['user_id']
		return self.user_id

	def load_company_users_data(self) -> dict:
		all_users_request_data = {
			'url':'https://app.7shifts.com/api/v1/users',
			'params':{
			    'deep': '1',
			    'offset': '0',
			    'active': '1', # 1 for employed, or 0 for previously employed
			}
		}
		company_user_data_json = self.session.get(**all_users_request_data).json()
		return company_user_data_json

	def load_work_locations(self) -> dict:
		user_locations_request_data = {
	    'url':f"https://app.7shifts.com/api/v2/company/139871/users/{self.user_id}/authorized_locations"
		}
		user_locations_json = self.session.get(**user_locations_request_data).json()
		return user_locations_json

	def load_shift_pool(self):
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
		shift_pool_json = self.session.post(**shift_offers_request_data).json()
		return shift_pool_json

	def run(self):
		self.login_success = self.login()
		self.account_data = self.load_account_data()
		self.company_users_data = self.load_company_users_data()
		self.work_locations = self.load_work_locations()
		self.shift_pool = self.load_shift_pool()

	def __repr__(self):
		return f"<DataCollector: {self.user_id}>"

seven_data = DataCollector()
seven_data.run()
print(seven_data.shift_pool)