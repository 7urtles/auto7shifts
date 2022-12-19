


import requests
import json

def login(session, email='charleshparmley@icloud.com',password='Earthday19!@22'):
	login_request_data = {
	    'url':'https://app.7shifts.com/users/login',
	    'data':{
	        '_method': 'POST',
	        'data[_Token][key]': 'cbd332b64ee4f15a967a692a4a237f3a',
	        'data[User][email]': email,
	        'data[User][password]': password,
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
	response_code = session.post(**login_request_data).status_code
	if response_code != 302:
		raise ValueError(f"[error]: Invalid stats code.\tExpected 302, got {response_code}")
	return True

def account_data(session):
	user_account_request_data = {
    	'url':"https://app.7shifts.com/api/v2/company/139871/account"
	}
	account_data_json = session.get(**user_account_request_data).json()
	user_id = account_data_json['data']['user_id']
	return user_id

def company_users_data(session):
	all_users_request_data = {
		'url':'https://app.7shifts.com/api/v1/users',
		'params':{
		    'deep': '1',
		    'offset': '0',
		    'active': '1', # 1 for employed, or 0 for previously employed
		}
	}
	company_user_data_json = session.get(**all_users_request_data).json()
	return company_user_data_json

def work_locations(user_id, session):
	user_locations_request_data = {
    'url':f"https://app.7shifts.com/api/v2/company/139871/users/{user_id}/authorized_locations"
	}
	user_locations_json = session.get(**user_locations_request_data).json()
	return user_locations_json

def shift_pool(session):
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
	shift_pool_json = session.post(**shift_offers_request_data).json()
	return shift_pool_json

# create new requests browsing session capable of maintaining login and auto handling cookies/headers
with requests.Session() as session:
	login(session)
	user_id = account_data(session)
	user_locations = work_locations(user_id,session)
	all_users = company_users_data(session)
	print(all_users)
	exit()
	available_shifts = shift_pool(session)
