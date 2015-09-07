import logging

import requests
from simplejson import JSONDecodeError


class EventSearch(object):
    BASE_SEARCH_URL = 'https://secure.berniesanders.com/page/event/search_results'
    SEARCH_DEFAULTS = {'radius': 100, 'radius_unit': 'mi', 'country': 'us'}
    ICS_PARAMS = {'mime': 'text/calendar', 'format': 'ical', 'wrap': 'no'}

    def __init__(self, zip_code, radius, radius_unit, country):
        self.zip_code = zip_code
        self.radius = radius or self.SEARCH_DEFAULTS['radius']
        self.radius_unit = radius_unit or self.SEARCH_DEFAULTS['radius_unit']
        self.country = country or self.SEARCH_DEFAULTS['country']
        self._search_results = []

    @property
    def results(self):
        self.execute_search()
        return self._search_results

    @property
    def search_params(self):
        return {
            'zip_radius[0]': self.zip_code,
            'zip_radius[1]': self.radius,
            'radius_unit': self.radius_unit,
            'country': self.country,
            'orderby': 'day',
            'format': 'json',
        }

    def execute_search(self):
        try:
            response_body = requests.get(self.BASE_SEARCH_URL, params=self.search_params).json()
            results = response_body['results']
        except JSONDecodeError:
            logging.warning('The response body of the search request could not be JSON-decoded')
        except KeyError:
            logging.warning('The response body of the search request was missing results')
        else:
            logging.info('Search returned %d results', len(results))
            self._search_results = results

    @classmethod
    def get_event_ics(cls, event):
        return requests.get(event['url'], params=cls.ICS_PARAMS).content

    @classmethod
    def from_config(cls, config_dict):
        search_config = config_dict.get('SEARCH', {})
        try:
            config_zip_code = search_config['ZIP_CODE']
        except KeyError:
            raise Exception('ZIP_CODE must be defined in config "SEARCH" section!')
        else:
            return cls(
                zip_code=config_zip_code,
                radius=search_config.get('RADIUS'),
                radius_unit=search_config.get('RADIUS_UNIT'),
                country=search_config.get('COUNTRY')
            )
