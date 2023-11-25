import os
import sys
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def checkSysPathAndAppend(path, stepBack = 0):
    if stepBack > 0:
        for istep in range(stepBack):
            if istep == 0:
                pathStepBack = path
            pathStepBack, filename = os.path.split(pathStepBack)
    else:
        pathStepBack = path

    if not pathStepBack in sys.path:
        sys.path.append(pathStepBack)

    return pathStepBack

folderFile, filename = os.path.split(os.path.realpath(__file__))
FOLDER_PROJECT = checkSysPathAndAppend(folderFile, 2)
FOLDER_CONFIG = os.path.join(FOLDER_PROJECT, 'config')
FOLDER_RECORD = os.path.join(FOLDER_PROJECT, 'player_record')
FOLDER_DATA = os.path.join(FOLDER_PROJECT, 'data')

import lib.DataProcessing as mylib

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
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH_CREDS, SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(PATH_TOKEN, "w") as token:
        token.write(creds.to_json())
    
    return creds

def sheet_read(service, spreadsheet_id, sheet_name, range):
  """
  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  # creds, _ = google.auth.default()
  
  # pylint: disable=maybe-no-member
  try:
    range_name = f"{sheet_name}!{range}"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    # rows = result.get("values", [])
    # print(f"{len(rows)} rows retrieved")


    return result
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error
    
if __name__ == "__main__":
  
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("log in...")
    creds = google_authen(FOLDER_CONFIG)

    print("build google sheet service...")
    service = build("sheets", "v4", credentials=creds)

    print("read data from sheet...")
    spreadsheet_id = "1hbDSWdrGu8dfTwmZQ0Avf7LMUoyTt4wGUw2Aw9g5YoU"

    print("write user_id to csv...")
    sheet_name = "userID"
    range_name = "A1:C300"
    sheet_user_id = sheet_read(service, spreadsheet_id, sheet_name, range_name)
    PATH_USER_ID = os.path.join(FOLDER_DATA, 'user_id', 'user_id_rf.csv')
    mylib.list2csv(PATH_USER_ID, sheet_user_id['values'], is_nested_list=True)

    print("write player log to csv...")
    sheet_name = "log"
    range_name = "A1:B100"
    sheet_log = sheet_read(service, spreadsheet_id, sheet_name, range_name)
    PATH_LOG = os.path.join(FOLDER_PROJECT, 'player_record', 'ggsheet','current_player_log.csv')
    mylib.list2csv(PATH_LOG, sheet_log['values'], is_nested_list=True)

    print("Finish")