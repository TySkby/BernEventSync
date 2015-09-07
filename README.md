# BernEventSync
Synchronize events from go.berniesanders.com to a Google Calendar

## Setup and configuration
1. Clone (or download and extract) this repository to your server
2. Create a Google Calendar (if you haven't already) that you want to sync with
3. Set up OAuth credentials for the Google Account authorized to manage your target Google Calendar:
    1. Go to https://console.developers.google.com
    2. Select "Create a Project" from the dropdown at the top of the page
    3. Name your project whatever you like
    4. Refresh the page and the select the project you just created from the same dropdown
    5. Select "APIs" under **APIs & auth** in the left-side menu
    6. Search for and select the **Calendar API** in the API Library
    7. Enable the Calendar API by clicking the "Enable API" button
    8. Select "Credentials" under **APIs & auth** in the left-side menu
    9. Add an OAuth 2.0 client id, configuring OAuth consent screen as-necessary
4. Once your credentials are configured, download them and save the downloading file to the `credentials` directory in this repository.  Name the file `client_secret.json`.
5. Open and edit `config.py` in the repository to modify and save changes to the following sections:
    1. **CALENDAR['id']:** Set this value if you know the ID of your Google Calendar.  If you don't, set it to `None`.
    2. **CALENDAR['name']:** If you set the above value to `None`, enter the name of your calendar here.  This is the same name you entered when creating your calendar in Step 2 of this guide.
    3. **SEARCH:** Set these values to strings that seem best to you.  In general, set `zip_code` to something appropriate to your needs- the rest of the values can be left untouched.
6. Install project requirements by running `pip install -r requirements.txt` in your console

## Running the program manually
1. In your console, navigate to the directory where you installed the repository
2. Run the following command: `python sync.py` to begin the processs of searching for events from Bernie Sanders' website and inserting them into your Google Calendar.
3. Repeat Step 2 whenever you want to update your calendar with new and updated events!

## Other uses:
- If you are maintaining a Google Calendar for a grassroots organization, it may be useful to run `sync.py` as a cron job (every 24 hours) to keep your organization's calendar up-to-date.

## Known issues/caveats:
- The JSON event data retrieved from go.berniesanders.com contain a non-standard timezone abbreviation (eg. "PDT" for Pacific Daylight-Savings Time) which is incompatible with Google Calendar's requirements that IANA timezone identifiers (eg. "America/Los_Angeles") be used.  The current workaround is to use the timezone configured on the target Google Calendar for all events.  Any suggestions or solutions would be most welcome!
- ??? Open an issue if you find one (or better yet, fork and submit a pull request)
