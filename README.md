# strava-club-segement
As Strava did renew their API it was no longer possible to pull leaderboards.

This repository pulls the leaderboards by using a headless chromedriver and logging into Strava. 

This code was used to pull club specific leaderboards, hence the XPath pointers are hard coded. It also updates a Google Spreadsheet in which non Strava Users can manually enter their times. The code then combines the Strava and Manual entries to a monthly/weekly leaderboard. Those cell numbers are also specified to the Sheet. If you are interested, I can give access to a template of that sheet.

The code is used in a sport challenge.
