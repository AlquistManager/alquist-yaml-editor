from __future__ import print_function
from states.state import State
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime

'''
try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
'''
flags = None

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Working Time'


class spreadsheet_add_time(State):
    # execute state
    def execute(self, request_data) -> dict:

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        spreadsheetId = '1rWqfCa3dSYg6CCXA-PEbyDs6cQkYC1UeJ8cgIfmX8RY'

        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
        sheets = sheet_metadata.get('sheets', '')

        username = request_data['context']['username']
        action = request_data['context']['action']

        error = False
        if action == "start":
            range_name = username + '!B12'
        elif action == "end":
            range_name = username + '!B1'
        else:
            error = True
            request_data['context']['error'] = True

        if not error:
            values = [
                [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ],
                # Additional rows ...
            ]
            body = {
                'values': values
            }
            value_input_option = "USER_ENTERED"
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheetId, range=range_name,
                valueInputOption=value_input_option, body=body).execute()

        request_data.update({'next_state': self.transitions.get('next_state', False)})
        return request_data


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.getcwd()
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-working-time.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
