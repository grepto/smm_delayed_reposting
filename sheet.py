from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_sheet_credentials():
    credentials = None
    if os.path.exists('gsheet_token.pickle'):
        with open('gsheet_token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server()
        with open('gsheet_token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


def get_sheet(spreadsheet_id, range_name):
    credentials = get_sheet_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    sheets = service.spreadsheets()
    result = sheets.values().get(spreadsheetId=spreadsheet_id,
                                 range=range_name,
                                 valueRenderOption='FORMULA').execute()
    values = result.get('values', [])
    return values


def update_sheet_cell(spreadsheet_id, cell_range, value):
    values = [[value]]
    body = {
        'values': values
    }
    credentials = get_sheet_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().update(spreadsheetId=spreadsheet_id,
                                   range=cell_range,
                                   valueInputOption='RAW',
                                   body=body).execute()
    values = result.get('values', [])
    return values


def main():
    pass


if __name__ == '__main__':
    main()
