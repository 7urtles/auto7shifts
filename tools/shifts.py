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
    shift_pool_id: str
    shift_offer_id: int
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
        return f"<Shift:{self.id} | {self.role['name']} | {self.location['address'].split(' ')[0]} | {self.start.split('T')[0]} | PoolID:{self.shift_pool_id}>"

# *******************************************************************************

@dataclass
class UserShift:
    id:str
    location_id:str
    user_id:str
    role_id:str
    department_id:str
    start:str
    end:str
    close:str
    bd:str
    notes:str
    draft:str
    open:str
    open_offer_type:str
    station:str
    station_name:str
    deleted:str
    last_published:str
    status:str
    start_iso:str
    end_iso:str
    last_published_iso:str
    company_id:str

    def dict(self) -> dict:
        return vars(self)

    def __repr__(self) -> str:
        return f"<UserShift:{self.id} | User:{self.user_id} | Role:{self.role_id} | Location:{self.location_id}>"

# *******************************************************************************

class ShiftPool:
    def __init__(self, pool_data:list):
        self.id = None
        self.shifts = {}
        self.update_pool(pool_data)
    
    def store_shifts(self):
        with open("shifts.csv", "a") as outfile:
            writer = csv.writer(outfile)
            for shift in self.shifts:
                writer.writerow(self.shifts[shift].dict())
    
    def update_pool(self, pool_data:list)->None:
        """
        Populates self.shifts dict with Shift objects using each found shifts id as the key and its data as the value.
        Shifts are added if the shift id is not in self.shifts
        """
        # shift_table = pool_data['data']['getShiftPool']['legacyShiftPoolOffers']
        for found_shift in pool_data:
            shift_id = found_shift['shift']['id']
            if shift_id in self.shifts:
                continue
            shift_offer_data = {
                'shift_pool_id' : found_shift['shiftPool']['id'],
                'shift_offer_id' : found_shift['shiftPool']['offerId']
            }
            found_shift['shift'].update(shift_offer_data)
            # if the key is not deleted, double underscore dict key will not match because of 
            #   name mangling on class attributes with double underscores
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
        self.get_locations()
    
    def get_locations(self)->None:
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

@dataclass
class Employee:
    id: str
    firstname: str
    mapping_id: str
    lastname: str
    birth_date: str
    user_type_id: str
    email: str
    photo: str
    mobile_phone: str
    home_phone: str
    hourly_wage: str
    skill_level: str
    wage_type: str
    max_weekly_hours: str
    payroll_id: str
    employee_id: str
    notes: str
    lang: str
    address: str
    city: str
    prov_state: str
    postal_zip: str
    appear_as_employee: str
    sms_me_schedules: str
    sms_me_shiftpool: str
    sms_me_shiftpool_requests: str
    sms_me_timeoff_requests: str
    sms_me_global_messages: str
    sms_me_employee_health_check: str
    sms_me_late_punch_in: str
    email_me_global_messages: str
    email_me_schedules: str
    email_me_shiftpool: str
    email_me_new_wall_posts: str
    email_me_timeoff_requests: str
    email_me_availability_changes: str
    email_me_shiftpool_requests: str
    email_me_punch_errors: str
    email_me_logbook_posts: str
    email_me_employee_health_check: str
    email_me_late_punch_in: str
    email_me_digest_stats: str
    active: str
    show_copy_previous_dialog: str
    push: str
    notify_ot_risk: str
    notify_ot_actual: str
    notify_break_alerts: str
    hire_date: str
    mobile_me_wall_posts: str
    mobile_me_logbook_posts: str
    subscribe_to_updates: str
    last_login: str
    invited: str
    invite_accepted: str
    created: str
    modified: str
    identity_id: str
    preferred_first_name: str
    preferred_last_name: str
    pronouns: str
    company_id: str
    invite_expiry: str
    invite_status: str

    def dict(self) -> dict:
        return vars(self)

    def __repr__(self) -> str:
        return f'<Employee id:{self.id}>'

# *******************************************************************************