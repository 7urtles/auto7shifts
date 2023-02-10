Auto7shifts v2

Second iteration of an automated shift pickup tool.


## Purpose:
--------
Some employee management tools have a feature to automatically claim work shifts as they come available.  
Currently the 7shifts employee management application does not have this feature.

Auto7shifts aims to fill that gap.

Since other employees of a company cannot auto claim shifts, an Auto7shifts user can potentially be the only  
employee within a company to to instantly claim shifts that come available.

This allows a user to have a significant increase in pay based on how much they are willing to work and   
how many shifts come available. Personal testing yielded an average pay increase of $300 a week. Not too shabby!


### Features:
---------
- Privelage Detection:
Companies possibly have multiple roles, positions, and locations.
The app will detect what the user has access to and provide selectable options accordingly.

- Day Selection:
Ability to specify what days a user would like to pick up shifts on.

- Schedule Detection:
The official 7shifts app allows the possibility for users to pick up shifts when the are already scheduled.
Auto7shifts will detect what days a user is already working and prevent accidental double scheduling issues.

- SMS Notifications via Twilio:  
If twilio is configured the app can send sms messages to the user notifying of the details of their new shift  
upon claiming it. Notification includes timeframe, date, role, position, and location of the claimed shift.
Setup instructions pending...

- Telegram Message Notifications:  
This feature requires the creation and setup of a Telegram bot.
Setup instructions pending...

- Web UI w/ Stripe payment portal:  
A entrepenurial user can use the included flask server frontend, serving it publically, to provide use  
of Auto7shifts as a service

- Device Discretion:  
Auto7shifts changes the applications user-agent in its request headers to normalize the apps appearance to  
7shifts official web app servers. However this is not necessary as 7shifts support and developer team have  
verified that Auto7shifts is compliant with their TOS, user, and api policies. 


## Usage:
------
Edit the included config.json
