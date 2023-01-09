
import calendar
import logging
from datetime import datetime, date

def shift_wanted(shift) -> str | bool:
    logging.debug(f"Checking shift: {shift.id}")
    logging.debug(shift)
    # Check if the shift role is one the user wants
    if shift.role not in user['roles']:
        return False
    # Check if the shift location is one the user wants
    if shift.location not in user['locations']:
        return False
    # Check if the shift day is one the user wants
    if shift.day not in user['days']:
        return False
    # If we made it here the found shift is acceptable to claim 
    return True

def check_role(shift):
    if shift.role['name'] not in app.shift_preferences["roles"]:
        logging.debug(f'Shift role not {app.shift_preferences["roles"]} {shift}')
        return False
    return True

def check_location(shift):
    if shift.role['location'] not in app.shift_preferences["locations"]:
        logging.info(f'Shift location not {app.shift_preferences["locations"]} {shift}')
        return False
    return True

def check_day(shift):
    if weekday not in app.shift_preferences["days"]:
        logging.debug(f"{weekday} not in {app.shift_preferences['days']}")
        logging.info(f"Shift day not {app.shift_preferences['days']} {shift}")
        return False
    return True

def convert_shift_date(shift_start_string:str) -> date:
    # Parse out the shift date
    date_string = date_string.split('T')[0]
    formatted_date = datetime.strptime(date_string, '%Y-%m-%d')
    return formatted_date.date()

def date_to_weekday(shift_date:datetime) -> str:
    return calendar.day_name[formatted_date.weekday()]

def store_shift(shift)->None:
    db.session.add(shift)
    db.session.commit()

def shift_not_stored(shift)->None:
    shift_exists = DroppedShift.query.filter_by(id=shift.id).first()
    if shift_exists:
        logging.debug(f"Shift: {shift.id} already in database.")
        return False
    return True

def format_shift(shift:dict) -> dict:
    shift_id = shift['id']

    shift.update({
        'shift_pool_id' : found_shift['shiftPool']['id'],
        'shift_offer_id' : found_shift['shiftPool']['offerId']
    })
    del shift['__typename']
    shift['user'] = shift['user']['userId']
    shift['location'] = shift['location']['address']
    shift['department'] = shift['department']['name']
    shift['role'] = shift['role']['id']
    shift['date'] = convert_shift_date(shift['start'])
    shift['day'] = date_to_weekday(shift['date'])
    return shift