import os

import oauth2client
from oauth2client import client
from oauth2client import tools

from config import config


try:
    import argparse as _argparse
    # Get CLI flags
    flags = _argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    # No CLI flags to get
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_STORAGE_DIR = config['AUTH']['CREDENTIAL_STORAGE_DIR']
CREDENTIAL_STORAGE_FILENAME = config['AUTH']['CREDENTIAL_STORAGE_FILENAME']
CLIENT_SECRET_FILENAME = config['AUTH']['CLIENT_SECRET_FILENAME']
APPLICATION_NAME = 'bernievent'


def get_credentials():
    credential_dir = get_storage_directory()
    credential_path = os.path.join(credential_dir, CREDENTIAL_STORAGE_FILENAME)
    client_secret_path = os.path.join(credential_dir, CLIENT_SECRET_FILENAME)

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_path, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to {}'.format(credential_path))
    return credentials


def get_storage_directory():
    if os.path.isabs(CLIENT_STORAGE_DIR):
        storage_dir = CLIENT_STORAGE_DIR
    else:
        storage_dir = os.path.join(os.getcwd(), CLIENT_STORAGE_DIR)

    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)

    return storage_dir
