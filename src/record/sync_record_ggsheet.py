import os
import sys
from datetime import datetime
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import pandas as pd

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

    list_value = result['values']

    return result, list_value
  
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error
  
def sheet_clear(service, spreadsheet_id, sheet_name, range):
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
        .clear(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    # rows = result.get("values", [])
    # print(f"{len(rows)} rows retrieved")

    # list_value = result['values']

    # return result, list_value
  
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error


def change_format_ts(timestamp, is_datetime=True):
    if is_datetime:
        timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
        timestamp_new = timestamp_datetime.strftime("%Y%m%d_%H%M%S")
    
    else:
        timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%d")
        timestamp_new = timestamp_datetime.strftime("%Y%m%d")

    return timestamp_new

def write_logday(list_data_row, log_type='player', filname_extend="logday.csv"):
    header_row = list_data_row[0]
    list_data_day = []
    list_data_day.append(header_row)
    n_row_log = len(list_data_row)
    for i in range(n_row_log):
        if i == 0:
            continue

        timestamp = list_data_row[i][0][0:10]
        data_row = list_data_row[i]
        if i == 1:
            list_data_day.append(data_row)

        elif i > 1:
            if timestamp == timestamp_prev:
                # same day
                list_data_day.append(data_row)
            
            else:
                # new day
                timestamp_new = change_format_ts(timestamp_prev, is_datetime=False)
                filename_gg_day = f'{timestamp_new}_{filname_extend}'
                PATH_LOG = os.path.join(FOLDER_PROJECT, 'record', log_type, 'ggsheet', filename_gg_day)
                mylib.list2csv(PATH_LOG, list_data_day, is_nested_list=True)    
                
                list_data_day = []
                list_data_day.append(header_row)
                list_data_day.append(data_row)

        if i == (n_row_log - 1):
            # last row
            timestamp_new = change_format_ts(timestamp, is_datetime=False)
            filename_gg_day = f'{timestamp_new}_{filname_extend}'
            PATH_LOG = os.path.join(FOLDER_PROJECT, 'record', log_type, 'ggsheet', filename_gg_day)
            mylib.list2csv(PATH_LOG, list_data_day, is_nested_list=True)   

        timestamp_prev = timestamp

if __name__ == "__main__":
  
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("google authen...")
    creds = google_authen(FOLDER_CONFIG)

    print("build google sheet service...")
    service = build("sheets", "v4", credentials=creds)

    # print("read data from sheet...")
    spreadsheet_id = "1hbDSWdrGu8dfTwmZQ0Avf7LMUoyTt4wGUw2Aw9g5YoU"

    print("sync user id...")
    sheet_name = "userID"
    range_name = "A1:E300"
    sheet_user_id, list_user_id = sheet_read(service, spreadsheet_id, sheet_name, range_name)
    PATH_USER_ID = os.path.join(FOLDER_DATA, 'user_id', 'user_id_rf.csv')
    mylib.list2csv(PATH_USER_ID, list_user_id, is_nested_list=True)

    print("sync player log...")
    sheet_name = "log"
    range_name = "A1:B300"
    sheet_log, list_data_row = sheet_read(service, spreadsheet_id, sheet_name, range_name)
    
    timestamp_log = list_data_row[-1][0]
    timestamp_log = change_format_ts(timestamp_log, is_datetime=True)

    filename_gg = f'{timestamp_log}_log_ggsheet.csv'
    PATH_LOG = os.path.join(FOLDER_PROJECT, 'record', 'player', 'ggsheet', 'raw', filename_gg)
    if not os.path.exists(PATH_LOG):
        mylib.list2csv(PATH_LOG, list_data_row, is_nested_list=True)
        write_logday(list_data_row, 'player', 'logday_player.csv')

    else:
        print("player log already up to date.")
    
    sheet_name = "log"
    n_row_loaded = len(list_data_row)
    range_name = f"A2:B{n_row_loaded}"
    if os.path.exists(PATH_LOG):
        print(f"found downloaded file {PATH_LOG} ")
        print(f"clearing player log {range_name}...")
        sheet_clear(service, spreadsheet_id, sheet_name, range_name)
    
    print("sync shuttlecock...")
    sheet_name = "shuttlecock_log"
    range_name = "A1:D50"
    sheet_shuttlecock, list_shuttlecock = sheet_read(service, spreadsheet_id, sheet_name, range_name)
    write_logday(list_shuttlecock, 'shuttlecock', 'logday_shuttlecock.csv')

    sheet_name = "shuttlecock_log"
    n_row_loaded = len(list_shuttlecock)
    range_name = f"A2:B{n_row_loaded}"
    if os.path.exists(PATH_LOG):
        print(f"found downloaded file {PATH_LOG} ")
        print(f"clearing shuttlecock_log {range_name}...")
        sheet_clear(service, spreadsheet_id, sheet_name, range_name)
   
    print("#----- Finish -----#")