import os 
# from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def google_authen(FOLDER_CONFIG):

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
            creds.refresh(Request())
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