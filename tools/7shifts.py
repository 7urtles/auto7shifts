import requests
import json 
from pprint import pprint
# TODO
# - function to generate cookies
# - integrate the below shift data retrieval method into the bot. 
#   this would aleviate the overhead of running a selenium browser instance to check for shifts
cookies = {
    'ajs_user_id': 'null',
    'ajs_group_id': 'null',
    'ajs_anonymous_id': '%22e920e24a-a3ec-480e-9e4e-acdca87cea2f%22',
    '_mkto_trk': 'id:818-ERA-322&token:_mch-7shifts.com-1660665844856-74010',
    '_clck': '1j14jyd|1|f42|0',
    '_hjSessionUser_221567': 'eyJpZCI6ImIzODFhNWExLTEzZWQtNTQ3Yi05N2UzLTU1YWQyOWU4ZTBjMiIsImNyZWF0ZWQiOjE2NjA2NjU4NDcyMjUsImV4aXN0aW5nIjp0cnVlfQ==',
    '_gaexp': 'GAX1.2.7IEdVwjDSweBvEzI0X6voA.19431.2',
    '_fbp': 'fb.1.1670999774079.1334316478',
    '_gid': 'GA1.2.1907825151.1670999774',
    '_hjSessionUser_2606334': 'eyJpZCI6IjllZjk2YmU4LTljNjYtNWE4OC1iZGY2LTZiN2Q4Y2RiYjhiOCIsImNyZWF0ZWQiOjE2NjA2NjU4NDQ5NDgsImV4aXN0aW5nIjp0cnVlfQ==',
    'intercom-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5': 'f94e3307-3c1f-40bf-b88d-25ee2207a423',
    'intercom-session-8d800f31374664bbfbce1b9cef164ebc9b5014f5': '',
    'intercom-device-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5': '9b3d707a-fd60-48b3-b280-692ff0ceb4b7',
    '_uetsid': '9af48bd07b7911edae8c09eed91c08a2',
    '_uetvid': '0cf755b01d7d11ed8f1309673c14c629',
    '_ga_QEFTJR8TVY': 'GS1.1.1670999773.1.1.1670999777.56.0.0',
    '_ga': 'GA1.2.1060665794.1660665845',
    'plan_combination': 'ada0c2c02653be4092f376bd0ed96254',
    'CakeCookie[shifts_login]': 'qv4iDQmz4ah6pcryHFxw79RWcBCAIPt1E5D4wTOpGblp6tuBP3zLwP5oZl7%2FI0%2BF0lqunXoFwWWvHnP9%2BqGHGKrRotw7P8qntH77J%2BkiRL5P%2F4M%2FYkokhQwvwJ0Li%2BdL81EjZDjWLbernhJPou49orY9DdwT4cg8x4kA',
    '7session': '93hvir62c9m1agjclkfkkitki1',
    'XSRF-TOKEN': 'd8e747cc945cc0a3b4b69fe50702b6da',
    '_gat': '1',
    '_gat_UA-8552753-1': '1',
    'mp_e955f41fc273a9c907d3d9afb36cfbc7_mixpanel': '%7B%22distinct_id%22%3A%204849459%2C%22%24device_id%22%3A%20%221850f59715871-062880b273e99e-163b3a75-1fa400-1850f59715919f4%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fapp.7shifts.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22app.7shifts.com%22%2C%22%24user_id%22%3A%204849459%2C%22company_id%22%3A%20%5B%0A%20%20%20%20139871%0A%5D%7D',
    '_hjIncludedInSessionSample': '1',
    '_hjSession_221567': 'eyJpZCI6IjVhOWFiNWQwLTBjZTYtNDQ3MS05YWNkLTc0YWU5NzRhMDJmZCIsImNyZWF0ZWQiOjE2NzEwMDY5MjYxNDQsImluU2FtcGxlIjp0cnVlfQ==',
    '_hjIncludedInPageviewSample': '1',
    '_hjAbsoluteSessionInProgress': '0',
    '_dd_s': 'rum=0&expire=1671007835163',
}
headers = {
    'Host': 'app.7shifts.com',
    # 'Content-Length': '1220',
    'Sec-Ch-Ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'X-Xsrf-Token': 'd8e747cc945cc0a3b4b69fe50702b6da',
    'Sec-Ch-Ua-Mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.95 Safari/537.36',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Origin': 'https://app.7shifts.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://app.7shifts.com/company/139871/shift_pool/up_for_grabs',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    # 'Cookie': 'ajs_user_id=null; ajs_group_id=null; ajs_anonymous_id=%22e920e24a-a3ec-480e-9e4e-acdca87cea2f%22; _mkto_trk=id:818-ERA-322&token:_mch-7shifts.com-1660665844856-74010; _clck=1j14jyd|1|f42|0; _hjSessionUser_221567=eyJpZCI6ImIzODFhNWExLTEzZWQtNTQ3Yi05N2UzLTU1YWQyOWU4ZTBjMiIsImNyZWF0ZWQiOjE2NjA2NjU4NDcyMjUsImV4aXN0aW5nIjp0cnVlfQ==; _gaexp=GAX1.2.7IEdVwjDSweBvEzI0X6voA.19431.2; _fbp=fb.1.1670999774079.1334316478; _gid=GA1.2.1907825151.1670999774; _hjSessionUser_2606334=eyJpZCI6IjllZjk2YmU4LTljNjYtNWE4OC1iZGY2LTZiN2Q4Y2RiYjhiOCIsImNyZWF0ZWQiOjE2NjA2NjU4NDQ5NDgsImV4aXN0aW5nIjp0cnVlfQ==; intercom-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5=f94e3307-3c1f-40bf-b88d-25ee2207a423; intercom-session-8d800f31374664bbfbce1b9cef164ebc9b5014f5=; intercom-device-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5=9b3d707a-fd60-48b3-b280-692ff0ceb4b7; _uetsid=9af48bd07b7911edae8c09eed91c08a2; _uetvid=0cf755b01d7d11ed8f1309673c14c629; _ga_QEFTJR8TVY=GS1.1.1670999773.1.1.1670999777.56.0.0; _ga=GA1.2.1060665794.1660665845; plan_combination=ada0c2c02653be4092f376bd0ed96254; CakeCookie[shifts_login]=qv4iDQmz4ah6pcryHFxw79RWcBCAIPt1E5D4wTOpGblp6tuBP3zLwP5oZl7%2FI0%2BF0lqunXoFwWWvHnP9%2BqGHGKrRotw7P8qntH77J%2BkiRL5P%2F4M%2FYkokhQwvwJ0Li%2BdL81EjZDjWLbernhJPou49orY9DdwT4cg8x4kA; 7session=93hvir62c9m1agjclkfkkitki1; XSRF-TOKEN=d8e747cc945cc0a3b4b69fe50702b6da; _gat=1; _gat_UA-8552753-1=1; mp_e955f41fc273a9c907d3d9afb36cfbc7_mixpanel=%7B%22distinct_id%22%3A%204849459%2C%22%24device_id%22%3A%20%221850f59715871-062880b273e99e-163b3a75-1fa400-1850f59715919f4%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fapp.7shifts.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22app.7shifts.com%22%2C%22%24user_id%22%3A%204849459%2C%22company_id%22%3A%20%5B%0A%20%20%20%20139871%0A%5D%7D; _hjIncludedInSessionSample=1; _hjSession_221567=eyJpZCI6IjVhOWFiNWQwLTBjZTYtNDQ3MS05YWNkLTc0YWU5NzRhMDJmZCIsImNyZWF0ZWQiOjE2NzEwMDY5MjYxNDQsImluU2FtcGxlIjp0cnVlfQ==; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _dd_s=rum=0&expire=1671007835163',
}
json_data = {
    'operationName': 'GetLegacyShiftPoolOffers',
    'variables': {
        'companyId': '139871',
        'cursor': None,
        'limit': 20,
    },
    'query': 'query GetLegacyShiftPoolOffers($companyId: ID!, $cursor: String, $limit: Int) {\n  getShiftPool(companyId: $companyId, cursor: $cursor, limit: $limit) {\n    legacyShiftPoolOffers {\n      ...LegacyShiftPoolOfferFragment\n      __typename\n    }\n    cursor {\n      prev\n      next\n      count\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment LegacyShiftPoolOfferFragment on LegacyShiftPoolOffer {\n  shiftPool {\n    id\n    offerType\n    offerId\n    offers {\n      id\n      firstname\n      lastname\n      photo\n      __typename\n    }\n    __typename\n  }\n  comments\n  shift {\n    id\n    start\n    end\n    open\n    user {\n      userId\n      firstName\n      lastName\n      photo\n      __typename\n    }\n    locationId\n    location {\n      address\n      timezone\n      __typename\n    }\n    department {\n      name\n      __typename\n    }\n    role {\n      id\n      name\n      color\n      __typename\n    }\n    __typename\n  }\n  location {\n    address\n    timezone\n    __typename\n  }\n  bids {\n    id\n    userId\n    __typename\n  }\n  __typename\n}\n',
}

# example json that would be returned by requesting the shift table data 
# shifts = json.load(open('mock_shift_table_response.json'))['data']['getShiftPool']['legacyShiftPoolOffers']

# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

class Shift:
    """
    TODO: add a day attribute
    """
    def __init__(self, shift_attrs:dict):
        self.id = shift_attrs['id']
        self.location = shift_attrs['location']['address']
        self.fname = shift_attrs['user']['firstName']
        self.lname = shift_attrs['user']['lastName']
        self.role = shift_attrs['role']['name']
        self.start = shift_attrs['start']
        self.end = shift_attrs['end']

# -------------------------------------------------------------------------------

class Shift_Pool:
    def __init__(self):
        self.shifts = {}
        self.update()

    def update(self)->None:
        """
        Fills self.shifts dict with Shift objects using the each found shifts id as a key.
        Shifts are only added to self.shifts if the shifts id does not already exist in the dict.
        Each shifts 
        """
        shift_pool_url = 'https://app.7shifts.com/gql'
        response = requests.post(shift_pool_url, cookies=cookies, headers=headers, json=json_data)
        shift_table = response.json()['data']['getShiftPool']['legacyShiftPoolOffers']

        for found_shift in shift_table:
            shift_id = found_shift['shift']['id']
            if shift_id not in self.shifts:
                self.shifts[shift_id] = Shift(found_shift['shift'])

# -------------------------------------------------------------------------------