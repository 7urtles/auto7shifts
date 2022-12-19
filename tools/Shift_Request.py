import requests
import json 
from pprint import pprint
# TODO
# - function to generate cookies
# - function to gather users scheduled shifts
# - function to gather users available locations
# - integrate the below shift data retrieval method into the bot. 
#   this would aleviate the overhead of running a selenium browser instance to check for shifts


cookies = {
    '_ga': 'GA1.2.1889191184.1670996571',
    '_gat': '1',
    '_gat_UA-8552753-1': '1',
    '_gid': 'GA1.2.1545688058.1671254176',
    '_hjAbsoluteSessionInProgress': '0',
    '_hjSessionUser_221567': 'eyJpZCI6IjVkMjFkOGE5LWMwNmQtNWU0MS04YTYyLTg4Zjc0ZjkxYmUzNyIsImNyZWF0ZWQiOjE2NzA5OTY1NzQ2MjgsImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjSession_221567': 'eyJpZCI6IjAwMzVmOTNiLTJlMmEtNGViNy1iZTc1LTMyM2QzMmU3ZWY0OCIsImNyZWF0ZWQiOjE2NzEyNjIyODgzMjIsImluU2FtcGxlIjp0cnVlfQ==',
    'amplitude_id_68421cd920bebdf3eeb2126694902e3b7shifts.com': 'eyJkZXZpY2VJZCI6ImEwYzBiNTNiLWNlM2UtNGQxYy04YzAyLWU2M2MzM2I2NDA5NlIiLCJ1c2VySWQiOiIyNDU4NTUwIiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNjcxMjYyMjg4ODQ2LCJsYXN0RXZlbnRUaW1lIjoxNjcxMjYyNzI4NjMzLCJldmVudElkIjoyMiwiaWRlbnRpZnlJZCI6NjUsInNlcXVlbmNlTnVtYmVyIjo4N30=',
    'mp_e955f41fc273a9c907d3d9afb36cfbc7_mixpanel': '%7B%22distinct_id%22%3A%204849459%2C%22%24device_id%22%3A%20%221850f284359404-0000401514b3898-3f626b4b-1fa400-1850f28435a2072%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.7shifts.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.7shifts.com%22%2C%22%24user_id%22%3A%204849459%2C%22company_id%22%3A%20%5B%0A%20%20%20%20139871%0A%5D%7D',
    '_dd_s': 'rum=0&expire=1671263628054',
    '_hjIncludedInSessionSample': '1',
    'plan_combination': 'ada0c2c02653be4092f376bd0ed96254',
    'XSRF-TOKEN': 'ce7bffc7d20791a27ce2294358a86122',
    '7session': 'n4qqkvgvhlnpnpoc51h3qjq4vo',
    'CakeCookie[shifts_login]': 'qv4iDQmz4ah6pcryHFxw79RWcBCAIPt1E5D4wTOpGblp6tuBP3zLwP5oZl7%2FI0%2BF0lqunXoFwWWvHnP9%2BqGHGKrRotw7P8qntH77J%2BkiRL5P%2F4M%2FYkokhQwvwJ0Li%2BdL81EjZDjWLbernhJPou49orY9DdwT4cg8x4kA',
    '_fbp': 'fb.1.1670996571616.20002134',
    'intercom-device-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5': '9f04418b-fe6d-43c3-ba26-1745cffb4933',
    'intercom-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5': '7d7fd244-428e-4a63-b5e2-3a87d1bc2583',
    'intercom-session-8d800f31374664bbfbce1b9cef164ebc9b5014f5': '',
    '_ga_QEFTJR8TVY': 'GS1.1.1671262286.7.1.1671262291.55.0.0',
    '_gaexp': 'GAX1.2.7IEdVwjDSweBvEzI0X6voA.19431.2',
    '_uetsid': 'ee2a1fe07dc911ed86a82fc9825b8f04',
    '_uetvid': '25d977907b7211edac9913ce88f50527',
    'ajs_anonymous_id': '%22bd36348d-2d07-4c94-9782-3e34fdcfa43e%22',
    'ajs_group_id': 'null',
    'ajs_user_id': 'null',
    '_hjSessionUser_2606334': 'eyJpZCI6IjFiMDZiOGNkLWE3OWQtNTU5MC04NjVmLTIwYTg3MTJlZjUxZSIsImNyZWF0ZWQiOjE2NzA5OTY1NzIzODcsImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjSession_2606334': 'eyJpZCI6IjM4YWNmZWRiLWUxZWItNDNhZS05N2Y3LTllMDg2ZGI3OTRiYiIsImNyZWF0ZWQiOjE2NzEyNjIyODYyNzUsImluU2FtcGxlIjpmYWxzZX0=',
    '_mkto_trk': 'id:818-ERA-322&token:_mch-7shifts.com-1670996572064-36738',
    '__zlcmid': '1DQlRtSLUhJZu6Y',
}

headers = {
    'Content-Type': 'application/json',
    'Accept': '*/*',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Host': 'app.7shifts.com',
    'Origin': 'https://app.7shifts.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Connection': 'keep-alive',
    'Referer': 'https://app.7shifts.com/company/139871/shift_pool/up_for_grabs',
    # 'Content-Length': '1220',
    # 'Cookie': '_ga=GA1.2.1889191184.1670996571; _gat=1; _gat_UA-8552753-1=1; _gid=GA1.2.1545688058.1671254176; _hjAbsoluteSessionInProgress=0; _hjSessionUser_221567=eyJpZCI6IjVkMjFkOGE5LWMwNmQtNWU0MS04YTYyLTg4Zjc0ZjkxYmUzNyIsImNyZWF0ZWQiOjE2NzA5OTY1NzQ2MjgsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_221567=eyJpZCI6IjAwMzVmOTNiLTJlMmEtNGViNy1iZTc1LTMyM2QzMmU3ZWY0OCIsImNyZWF0ZWQiOjE2NzEyNjIyODgzMjIsImluU2FtcGxlIjp0cnVlfQ==; amplitude_id_68421cd920bebdf3eeb2126694902e3b7shifts.com=eyJkZXZpY2VJZCI6ImEwYzBiNTNiLWNlM2UtNGQxYy04YzAyLWU2M2MzM2I2NDA5NlIiLCJ1c2VySWQiOiIyNDU4NTUwIiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNjcxMjYyMjg4ODQ2LCJsYXN0RXZlbnRUaW1lIjoxNjcxMjYyNzI4NjMzLCJldmVudElkIjoyMiwiaWRlbnRpZnlJZCI6NjUsInNlcXVlbmNlTnVtYmVyIjo4N30=; mp_e955f41fc273a9c907d3d9afb36cfbc7_mixpanel=%7B%22distinct_id%22%3A%204849459%2C%22%24device_id%22%3A%20%221850f284359404-0000401514b3898-3f626b4b-1fa400-1850f28435a2072%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.7shifts.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.7shifts.com%22%2C%22%24user_id%22%3A%204849459%2C%22company_id%22%3A%20%5B%0A%20%20%20%20139871%0A%5D%7D; _dd_s=rum=0&expire=1671263628054; _hjIncludedInSessionSample=1; plan_combination=ada0c2c02653be4092f376bd0ed96254; XSRF-TOKEN=ce7bffc7d20791a27ce2294358a86122; 7session=n4qqkvgvhlnpnpoc51h3qjq4vo; CakeCookie[shifts_login]=qv4iDQmz4ah6pcryHFxw79RWcBCAIPt1E5D4wTOpGblp6tuBP3zLwP5oZl7%2FI0%2BF0lqunXoFwWWvHnP9%2BqGHGKrRotw7P8qntH77J%2BkiRL5P%2F4M%2FYkokhQwvwJ0Li%2BdL81EjZDjWLbernhJPou49orY9DdwT4cg8x4kA; _fbp=fb.1.1670996571616.20002134; intercom-device-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5=9f04418b-fe6d-43c3-ba26-1745cffb4933; intercom-id-8d800f31374664bbfbce1b9cef164ebc9b5014f5=7d7fd244-428e-4a63-b5e2-3a87d1bc2583; intercom-session-8d800f31374664bbfbce1b9cef164ebc9b5014f5=; _ga_QEFTJR8TVY=GS1.1.1671262286.7.1.1671262291.55.0.0; _gaexp=GAX1.2.7IEdVwjDSweBvEzI0X6voA.19431.2; _uetsid=ee2a1fe07dc911ed86a82fc9825b8f04; _uetvid=25d977907b7211edac9913ce88f50527; ajs_anonymous_id=%22bd36348d-2d07-4c94-9782-3e34fdcfa43e%22; ajs_group_id=null; ajs_user_id=null; _hjSessionUser_2606334=eyJpZCI6IjFiMDZiOGNkLWE3OWQtNTU5MC04NjVmLTIwYTg3MTJlZjUxZSIsImNyZWF0ZWQiOjE2NzA5OTY1NzIzODcsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_2606334=eyJpZCI6IjM4YWNmZWRiLWUxZWItNDNhZS05N2Y3LTllMDg2ZGI3OTRiYiIsImNyZWF0ZWQiOjE2NzEyNjIyODYyNzUsImluU2FtcGxlIjpmYWxzZX0=; _mkto_trk=id:818-ERA-322&token:_mch-7shifts.com-1670996572064-36738; __zlcmid=1DQlRtSLUhJZu6Y',
    'Priority': 'u=3, i',
    'x-xsrf-token': 'ce7bffc7d20791a27ce2294358a86122',
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


# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"operationName":"GetLegacyShiftPoolOffers","variables":{"companyId":"139871","cursor":null,"limit":20},"query":"query GetLegacyShiftPoolOffers($companyId: ID!, $cursor: String, $limit: Int) {\\n  getShiftPool(companyId: $companyId, cursor: $cursor, limit: $limit) {\\n    legacyShiftPoolOffers {\\n      ...LegacyShiftPoolOfferFragment\\n      __typename\\n    }\\n    cursor {\\n      prev\\n      next\\n      count\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment LegacyShiftPoolOfferFragment on LegacyShiftPoolOffer {\\n  shiftPool {\\n    id\\n    offerType\\n    offerId\\n    offers {\\n      id\\n      firstname\\n      lastname\\n      photo\\n      __typename\\n    }\\n    __typename\\n  }\\n  comments\\n  shift {\\n    id\\n    start\\n    end\\n    open\\n    user {\\n      userId\\n      firstName\\n      lastName\\n      photo\\n      __typename\\n    }\\n    locationId\\n    location {\\n      address\\n      timezone\\n      __typename\\n    }\\n    department {\\n      name\\n      __typename\\n    }\\n    role {\\n      id\\n      name\\n      color\\n      __typename\\n    }\\n    __typename\\n  }\\n  location {\\n    address\\n    timezone\\n    __typename\\n  }\\n  bids {\\n    id\\n    userId\\n    __typename\\n  }\\n  __typename\\n}\\n"}'
#response = requests.post('https://app.7shifts.com/gql', cookies=cookies, headers=headers, data=data)
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

        def __repr__(self):
            return '<Shift id:%r>' % self.id

# -------------------------------------------------------------------------------

class Shift_Pool():
    def __init__(self):
        self.shifts = {}
        self.update()

    def update(self)->None:
        """
        Populates self.shifts dict with Shift objects using each found shifts id as the key and its data as the value.
        Shifts are added if the shift id is not in self.shifts
        
        """
        session = requests.Session()
        shift_pool_url = 'https://app.7shifts.com/gql'
        response = session.post(shift_pool_url, cookies=cookies, headers=headers, json=json_data)
        shift_table = response.json()['data']['getShiftPool']['legacyShiftPoolOffers']
        print(shift_table)
        for found_shift in shift_table:
            shift_id = found_shift['shift']['id']
            if shift_id not in self.shifts:
                self.shifts[shift_id] = Shift(found_shift['shift'])
pool = Shift_Pool()
print(list(pool.shifts.values())[0].id)
# -------------------------------------------------------------------------------