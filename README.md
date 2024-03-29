# Auto7shifts
 
Some employee management tools have a feature to automatically claim work as it comes available.

Auto7shifts provides that functionality to a user giving them an edge above their peers.

If other employees of a company cannot auto claim shifts, an Auto7shifts user can be the only  
employee within a company to automatically claim shifts as they come available.

This allows a user to have a significant increase in pay based on how much they are willing to work and   
how many shifts come available. Testing showed a users work opportunity increase by 30% on average. 
<br>

## Current Features:

- Privelage Detection:  
Companies possibly have multiple roles, positions, and locations.
The app will detect what the user has access to and provide selectable options accordingly.

- Day Selection:  
Ability to specify what days a user would like to pick up shifts on.

- Schedule Detection:  
The official 7shifts app allows the possibility for users to pick up shifts when the are already scheduled.
Auto7shifts will detect what days a user is already working and prevent accidental double scheduling issues.

- SMS Notifications:  
If Twilio is configured the app can send sms messages to the user notifying of the details of their new shift  
upon claiming it. Notification includes timeframe, date, role, position, and location of the claimed shift.  
Setup instructions pending...

- Device Discretion:  
Auto7shifts changes the applications user-agent in its request headers to normalize the apps appearance to  
7shifts official web app servers. However this is not necessary and 7shifts support has verified their TOS, user, 
and api policies are not being violated.
<br>

- Logging & Data Storage
Logging is set to INFO level by default & ogfile can be found in auto7shifts/logs
User account creation is currently disabled. Found shifts get stored into a simple sqlite3 database

## Setup:
1. Set up the necessary accounts (instructions below)
2. Clone this repository, installing necessary dependancies
```
git clone https://github.com/chparmley/auto7shifts.git
cd auto7shifts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Edit the included config.json with relevant account information and keys
4. Run
```
python3 cli.py
```
<br>
## SMS Notifications
Twilio setup is required. Each sms costs less than a penny. 
ROI should be acceptable.
Free methods are being explored.  

After creating an account setting up an sms service can be done here:  
https://console.twilio.com/us1/develop/sms/services

Once a messaging service is configured the callback url may be set up by going to:
Develop -> Sender Pool -> and clicking the phone number you registered.

This functionality requries setting the above phone number as your 7shifts contact number, along with  
switching from push to sms notifications within the 7shifts application.  
This is automatically done by Auto7shifts.

The 'TWILIO_ENDPOINT' variable is used to protect the applications callback url which prevents unauthorized triggering  
of the applications messaging system and is already set for you.  

Necessary keys below can be found on the Twilio home console.  

| Key | Example |
| ------------- | ------------- |
| TWILIO_ACCOUNT_SID  | 'pk_live_notAnAcutalKey'  |
| TWILIO_AUTH_TOKEN  | 'sk_live_notAnAcutalKey'  |
| TWILIO_PHONE_NUMBER  | '+18887776666'  |
| USER_PHONE_NUMBER  | '+18887776666'  |

The workflow for sms notifications is as such:
1. 7Shifts sends notification contents as an sms to Twilio triggering a webhook event
2. Twilio sends the notification contents to the applications callback endpoint activiting its functionality
3. If a shift is claimed its details are parsed by the application and sent to the user.
