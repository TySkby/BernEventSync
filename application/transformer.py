import hashlib
from dateutil import parser as dateutil_parser
from HTMLParser import HTMLParser


class EventTransformer(object):
    GOOGLE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
    ID_HASH_SUFFIX = 'BernEventSync'

    def __init__(self, raw_data, raw_ics, default_timezone, hash_key):
        self.raw_data = raw_data
        self.ics_data = self.ics_to_dict(raw_ics)
        self.default_timezone = default_timezone
        self.hash_key = hash_key
        self.html_parser = HTMLParser()

    @staticmethod
    def ics_to_dict(raw_ics):
        ics_data = {}
        for line_item in raw_ics.splitlines():
            try:
                key, value = line_item.split(':')
            except ValueError:
                continue
            else:
                if key.isupper():
                    ics_data[key] = value
        return ics_data

    @property
    def transformed(self):
        # TODO: Need a better solution than always using calendar timeZone value for events
        transformed_data = {
            'id': self.unique_id,
            'summary': self.ics_data.get('SUMMARY') or self.raw_data['name'],
            'description': self.html_parser.unescape('{main_description}\n\nLink: {url}'.format(
                main_description=(self.ics_data['DESCRIPTION'] or self.raw_data['description']),
                url=self.raw_data['url']
            )),
            'location': self.ics_data['LOCATION'] or self.build_location(self.raw_data),
            'start': {
                'dateTime': self.parse_datetime_from_raw_data(
                    self.raw_data.get('start_dt'),
                    self.raw_data.get('start_day'),
                    self.raw_data.get('start_time'),
                    self.ics_data.get('DTSTART'),
                ).strftime(self.GOOGLE_DATETIME_FORMAT),
                'timeZone': self.default_timezone,
            },
            'end': {
                'dateTime': self.parse_datetime_from_raw_data(
                    self.raw_data.get('end_dt'),
                    self.raw_data.get('start_day'),
                    self.raw_data.get('end_time'),
                    self.ics_data.get('DTEND')
                ).strftime(self.GOOGLE_DATETIME_FORMAT),
                'timeZone': self.default_timezone,
            }
        }
        return transformed_data

    @staticmethod
    def parse_datetime_from_raw_data(dt_string=None, date_string=None, time_string=None, ics_dt=None):
        if dt_string:
            try:
                return dateutil_parser.parse(dt_string)
            except ValueError:
                pass

        if date_string and time_string:
            try:
                return dateutil_parser.parse('{date}T{time}'.format(date=date_string, time=time_string))
            except ValueError:
                pass

        if ics_dt:
            try:
                return dateutil_parser.parse(ics_dt)
            except ValueError:
                pass

        return None

    @staticmethod
    def build_location(raw_data):
        components = [
            raw_data.get('venue_name'),
            raw_data.get('venue_addr1'),
            raw_data.get('venue_addr2'),
            raw_data.get('venue_city'),
            raw_data.get('venue_state_cd'),
            raw_data.get('venue_zip')
        ]
        return ', '.join([item for item in components if item])

    @property
    def unique_id(self):
        return hashlib.md5('{key}{event_id}{suffix}'.format(
            key=self.hash_key,
            event_id=str(self.raw_data['id']),
            suffix=self.ID_HASH_SUFFIX
        )).hexdigest()
