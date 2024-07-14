import os
import json

# import google.auth
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

def read_json(pathFile, mode='r'):
    f = open(pathFile, mode)
    dict_json = json.load(f)
    f.close()

    return dict_json

def google_authen(FOLDER_CONFIG, SCOPES):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    PATH_CREDS = os.path.join(FOLDER_CONFIG, 'credentials.json')
    PATH_TOKEN = os.path.join(FOLDER_CONFIG, "token.json")
    if os.path.exists(PATH_TOKEN):
        creds = Credentials.from_authorized_user_file(PATH_TOKEN, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print("credential not valid !")
        if creds and creds.expired and creds.refresh_token:
            print("credential refresh...")
            # creds.refresh(Request())
            os.remove(PATH_TOKEN)
        else:
            print("Install app flow and run local server...")
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH_CREDS, SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(PATH_TOKEN, "w") as token:
        token.write(creds.to_json())
    
    return creds

def get_credentials(FOLDER_CONFIG, SCOPES, method='service_account', filename_json_key=None):
    if method == 'authen':
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        print("google authen...")
        credentials = google_authen(FOLDER_CONFIG)

    elif method == 'service_account':
        if filename_json_key is None:
            raise ValueError(f'please input filename of json key: {filename_json_key}')

        from google.oauth2.service_account import Credentials

        PATH_CRED_SERVICE_ACC = os.path.join(FOLDER_CONFIG, filename_json_key)
        # service_account_info = json.load(open('service_account.json'))
        service_account_info = read_json(PATH_CRED_SERVICE_ACC)
        credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    return credentials