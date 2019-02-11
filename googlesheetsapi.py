'''
Collection of functions to interact with Google Sheets
'''

import pickle
import os.path

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def authenticate():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.

    Returns:
        creds: google.oauth2.credentials.Credentials, Google API OAuth Credentials
    """
    creds = None

    # If modifying these scopes, delete the file token.pickle.
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_spreadsheets(credentials: dict):
    '''
    Get spreadsheets object

    Args:
        credentials: google.oauth2.credentials.Credentials, Google API OAuth Credentials

    Returns:
        spreadhseets: Google spreadsheets object
    '''
    # Call the Sheets API
    service = build('sheets', 'v4', credentials=credentials)
    return service.spreadsheets()


def get_spreadsheet_values(spreadsheets):
    '''
    Gets spreadhsset values object. Allowd manipulations such as append

    Args:
        spreadsheets: googleapiclient.discovery.Resource, Google API spreadsheets object

    Returns:
        values: Google API spreadhseets values object
    '''
    return spreadsheets.values() # NOTE: Return values object  


def get_range(spreadsheets, sheet_id: str, range_name: str):
    '''
    Get a specific range within a Google Sheet

    Args:
        spreadsheets: dict, Google API spreadsheets object
        sheet_id: Google sheet ID (found in sheet URL)
        range_name: Sheet Range, eg "A1:B4"

    Examples:
        TODO
    '''
    range_values = spreadsheets.values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute() # NOTE: return response dict
    return range_values  


if __name__ == '__main__':
    sid = '1jk_6MgIPxM0ijm3heWL3AqoJiPXdySJhbRnH7AVhH-U'
    range_name = 'Sheet1!A:M'
    creds = authenticate()
    sheets = get_spreadsheets(creds)
    sheet_values = get_spreadsheet_values(sheets)
    # sheet = get_range(spreadsheets=spreadsheets, sheet_id=sid, range_name=range_name)
    value_input_option = 'USER_ENTERED'
    insert_data_option = 'INSERT_ROWS'
    # include_values_in_response = True
    body = {
        'range': range_name,
        'values': [
            ['test', 'test', 'test']
        ]
    }
    request = sheet_values.append(spreadsheetId=sid, range=range_name, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=body)
    response = request.execute()
    from pprint import pprint
    pprint(response)



    # columns = sheet['values'][0]
    # data = sheet['values'][1:]
    # df = pd.DataFrame(data=data, columns=columns)
    # print(df)
    # values = columns + df.values.tolist() # XXX likely not faster than values.insert(0, columns)
    # # values.insert(0, columns) # can we use a deque here? is there a way to turn a df into a deque then insert columns left?
    # print(values)
