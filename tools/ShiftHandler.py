import requests
import json
import csv
from DataScraper import DataCollector
# -------------------------------------------------------------------------------

class Shift:
    """
    TODO: add a day attribute
    """
    def __init__(self, shift_attrs:dict):
        self.data = {
            "id" : shift_attrs['id'],
            "location" : shift_attrs['location']['address'],
            "owner_id" : shift_attrs['user']['userId'],
            "role" : shift_attrs['role']['name'],
            "start" : shift_attrs['start'],
            "end" : shift_attrs['end'],
        }

        def __repr__(self):
            return '<Shift id:%r>' % self.data['id']

# -------------------------------------------------------------------------------

class ShiftPool():
    def __init__(self, pool_data):
        self.id = None
        self.pool_data = pool_data
        self.shifts = {}
        self.create_pool()


    def store_shifts(self):
        with open("shifts.csv", "a") as outfile:
            writer = csv.writer(outfile)
            for shift in self.shifts:
                writer.writerow(self.shifts[shift].data.values())


    def create_pool(self)->None:
        """
        Populates self.shifts dict with Shift objects using each found shifts id as the key and its data as the value.
        Shifts are added if the shift id is not in self.shifts
        
        """
        shift = self.pool_data['data']['getShiftPool']['legacyShiftPoolOffers'][0]
        shift_table = self.pool_data['data']['getShiftPool']['legacyShiftPoolOffers']
        for found_shift in shift_table:
            shift_id = found_shift['shift']['id']
            if shift_id not in self.shifts:
                self.shifts[shift_id] = Shift(found_shift['shift'])

    def __repr__(self):
            return '<ShiftPool id:0>'# % self.id

# -------------------------------------------------------------------------------


with open("mock_shift_table_response.json","r") as file:
    jsonData = json.load(file)

data = DataCollector('charleshparmley@icloud.com','Earthday19!@22')

print('Logging in')

# data.login_success = data.login()

# if not data.login_success:
#     raise(ValueError('Could not log in'))

print('Login Success')
print('Loading Pool Data')

data.shift_pool = jsonData

if not data.shift_pool:
    raise(ValueError('Shift Pool Not Found'))

print('Shift Table Found')
print('Creating ShiftPool')

pool = ShiftPool(data.shift_pool)

if not pool.shifts:
    raise(ValueError('Pool Empty'))
pool.store_shifts()
print(pool.shifts['524472221'])
