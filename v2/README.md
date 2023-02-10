Auto7shifts v2

Second iteration of an automated shift pickup tool.


Purpose:
--------
Some employee management tools have a feature to automatically claim work shifts as they come available.  
Currently the 7shifts employee management application does not have this feature.

Auto7shifts aims to fill that gap.

Since other employees of a company cannot auto claim shifts, an Auto7shifts user can potentially be the only
employee within a company to to instantly claim shifts that come available.

This allows a user to have a significant increase in pay based on how much they are willing to work and how many shifts
come available. Personal testing yielded an average pay increase of $300 a week. Not too shabby!

Features:
---------
-Privelage detection:
Companies possibly have multiple roles, positions, and locations.
The app will detect what the user has access to and provide selectable options accordingly.

-Day Selection:
Ability to specify what days a user would like to pick up shifts on

-Schedule detection:
The official 7shifts app allows the possibility for users to pick up shifts when the are already scheduled.
Auto7shifts will detect what days a user is already working and prevent accidental double scheduling issues.

Usage:
------
Edit the included config.json
