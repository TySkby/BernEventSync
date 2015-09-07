import logging

from googleapiclient.errors import HttpError

from application.event_search import EventSearch
from application.calendar import GoogleCalendar
from application.transformer import EventTransformer
from config import config


def extract():
    search = EventSearch.from_config(config)
    return (result for result in search.results)


def transform(source_result, target_calendar):
    return EventTransformer(
        raw_data=source_result,
        raw_ics=EventSearch.get_event_ics(source_result),
        default_timezone=target_calendar.calendar_timezone,
        hash_key=target_calendar.calendar_id
    ).transformed


def load(event_data, target_calendar, action):
    try:
        if action == 'insert':
            target_calendar.insert_event(event_data)
        elif action == 'update':
            target_calendar.update_event(event_data)
        else:
            raise Exception('Received unknown load action: "{}"'.format(action))
    except HttpError as e:
        logging.exception(e)


def run_etl(limit=None):
    target_calendar = GoogleCalendar()
    known_event_ids = target_calendar.get_known_event_ids()

    num_processed = 0
    for result_to_process in extract():
        transformed_event = transform(result_to_process, target_calendar)
        load(
            event_data=transformed_event,
            target_calendar=target_calendar,
            action='update' if transformed_event['id'] in known_event_ids else 'insert',
        )

        num_processed += 1
        if limit and num_processed >= limit:
            break


if __name__ == '__main__':
    run_etl()
