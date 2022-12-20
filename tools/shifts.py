from dataclasses import dataclass

# *******************************************************************************

@dataclass
class User:
    identity_id: str
    user_id: str
    company_id: str
    user_type: str
    first_name: str
    last_name: str
    email: str
    photo: str
    language: str
    home_phone: str
    mobile_phone: str
    birth_date: str
    punch_id: str
    is_canceled: str
    is_trial: str
    is_active: str
    has_password: str
    third_party_auth_names: str
    company: str
    companies: str
    locations: str
    departments: str
    roles: str
    features: str
    plan: str
    trial_plan: str
    permissions: str
    settings: str
    ab_tests: str
    billing_system: str
    account_expiry: str

    def dict(self) -> dict:
        return vars(self)

    def __repr__(self) -> str:
        return f'<Shift id:{self.id}>'

# *******************************************************************************

@dataclass
class Shift:
    id: str
    start: str
    end: str
    open: str
    user: str
    locationId: str
    location: str
    department: str
    role: str
    typename: str

    def dict(self) -> dict:
        return vars(self)

    def __repr__(self) -> str:
        return f'<Shift id:{self.id}>'

# *******************************************************************************

class ShiftPool:
    def __init__(self, pool_data:dict):
        self.id = None
        self.pool_data = pool_data
        self.shifts = {}
        self.create_pool()
    
    def store_shifts(self):
        with open("shifts.csv", "a") as outfile:
            writer = csv.writer(outfile)
            for shift in self.shifts:
                writer.writerow(self.shifts[shift].dict())
    
    def create_pool(self)->None:
        """
        Populates self.shifts dict with Shift objects using each found shifts id as the key and its data as the value.
        Shifts are added if the shift id is not in self.shifts
        """
        # shift_table = self.pool_data['data']['getShiftPool']['legacyShiftPoolOffers']
        for found_shift in self.pool_data:
            shift_id = found_shift['shift']['id']
            if shift_id not in self.shifts:
                # if the key is not deleted, double underscore dict keys will not match name mangled class attributes
                found_shift['shift']['typename'] = found_shift['shift']['__typename']
                del found_shift['shift']['__typename']
                self.shifts[shift_id] = Shift(**found_shift['shift'])

    
    def __repr__(self):
            return '<ShiftPool id:0>'# % self.id

# *******************************************************************************

class UserLocations:
    def __init__(self, location_data:dict):
        self.id = None
        self.location_data = location_data
        self.locations = {}
        self.create_company()
    
    def create_company(self)->None:
        """
        Populates self.locations dict with Location objects using each found locations id as the key and its data as the value.
        Locations are added if the shift id is not in self.locations
        """
        for location in self.location_data:
            if location['id'] not in self.locations:
                self.locations[location['id']] = Location(**location)

    def __repr__(self):
            return '<Company id:0>'# % self.id

# *******************************************************************************

@dataclass
class Location:
    id: str
    company_id: str
    name: str
    country: str
    state: str
    city: str
    formatted_address: str
    lat: str
    lng: str
    place_id: str
    timezone: str
    timezone_updated: str
    hash: str
    mapping_id: str
    department_based_budget: str
    holiday_pay: str
    auto_send_log_book_time: str
    mon_hours_close: str
    tue_hours_close: str
    wed_hours_close: str
    thu_hours_close: str
    fri_hours_close: str
    sat_hours_close: str
    sun_hours_close: str
    mon_hours_open: str
    tue_hours_open: str
    wed_hours_open: str
    thu_hours_open: str
    fri_hours_open: str
    sat_hours_open: str
    sun_hours_open: str
    mon_is_closed: str
    tue_is_closed: str
    wed_is_closed: str
    thu_is_closed: str
    fri_is_closed: str
    sat_is_closed: str
    sun_is_closed: str
    shift_feedback: str
    message: str
    created: str
    modified: str

    def dict(self) -> dict:
        return vars(self)

    def __repr__(self) -> str:
        return f'<Location: {self.id}>'

# *******************************************************************************    