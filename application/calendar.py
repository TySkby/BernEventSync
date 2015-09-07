import httplib2

from apiclient import discovery

from application import auth
from config import config


class GoogleCalendar(object):
    def __init__(self):
        self.credentials = auth.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=self.http)
        self._calendar_data = self.get_calendar()
        try:
            self.calendar_id = self._calendar_data['id']
        except KeyError:
            raise Exception('Could not determine a valid Google Calendar ID!  Please check config settings.')
        self.calendar_timezone = self._calendar_data['timeZone']

    def get_calendar(self):
        if config['CALENDAR'].get('id'):
            return self._get_calendar_by_id(config['CALENDAR']['id'])
        elif config['CALENDAR'].get('name'):
            return self._get_calendar_id_by_name(config['CALENDAR']['name'])
        else:
            raise Exception(
                'An "id" or "name" value must be configured in the "CALENDAR" config section'
            )

    def _get_calendar_by_id(self, calendar_id):
        return self.service.calendars().get(calendarId=calendar_id).execute()

    def _get_calendar_id_by_name(self, name):
        calendar_list = self.service.calendarList().list().execute()
        for calendar in calendar_list['items']:
            if calendar.get('summary') == name:
                return calendar
        raise Exception('No calendar "{}" was found'.format(name))

    def get_known_events(self):
        known_events = []
        page_token = None
        while True:
            events = self.service.events().list(calendarId=self.calendar_id, pageToken=page_token).execute()
            known_events.extend(events['items'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        return known_events

    def get_known_event_ids(self):
        return [event['id'] for event in self.get_known_events()]

    def insert_event(self, event):
        self.service.events().insert(calendarId=self.calendar_id, body=event).execute()

    def update_event(self, event):
        event_id = event.pop('id')
        self.service.events().patch(calendarId=self.calendar_id, eventId=event_id, body=event).execute()

    def delete_event(self, event):
        self.service.events().delete(calendarId=self.calendar_id, eventId=event['id']).execute()
