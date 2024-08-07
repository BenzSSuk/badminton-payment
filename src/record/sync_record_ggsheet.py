import os
from os.path import join as pjoin
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

import lib as mylib

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

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

def write_logday(list_data_row, FOLDER_SAVE='cloud_log', log_type='player'):
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
                filename_gg_day = f'{timestamp_new}_logday_{log_type}.csv'

                PATH_LOG = os.path.join(FOLDER_SAVE, filename_gg_day)
                mylib.list2csv(PATH_LOG, list_data_day, is_nested_list=True)    
                
                list_data_day = []
                list_data_day.append(header_row)
                list_data_day.append(data_row)

        if i == (n_row_log - 1):
            # last row
            timestamp_new = change_format_ts(timestamp, is_datetime=False)
            filename_gg_day = f'{timestamp_new}_logday_{log_type}.csv'
            PATH_LOG = os.path.join(FOLDER_SAVE, filename_gg_day)
            mylib.list2csv(PATH_LOG, list_data_day, is_nested_list=True)   

        timestamp_prev = timestamp

if __name__ == "__main__":
  
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("google authen...")
    creds = mylib.get_credentials(FOLDER_CONFIG, SCOPES, method='service_account', filename_json_key='admin01.json')

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
    sheet_log, list_data_row_player = sheet_read(service, spreadsheet_id, sheet_name, range_name)
    
    if len(list_data_row_player) > 1:
        timestamp_log = list_data_row_player[-1][0]
        timestamp_log = change_format_ts(timestamp_log, is_datetime=True)

        filename_gg = f'{timestamp_log}_log_ggsheet.csv'
        PATH_LOG = os.path.join(FOLDER_PROJECT, 'data', 'cloud', 'player', filename_gg)
        if not os.path.exists(PATH_LOG):
            mylib.list2csv(PATH_LOG, list_data_row_player, is_nested_list=True)
            FOLDER_SAVE = pjoin(FOLDER_PROJECT, 'record', 'player', 'ggsheet')
            if not os.path.exists(FOLDER_SAVE):
                os.makedirs(FOLDER_SAVE)
            write_logday(list_data_row_player, FOLDER_SAVE, 'player')

        else:
            print("player log already up to date.")
        
        sheet_name = "log"
        n_row_loaded = len(list_data_row_player)
        range_name = f"A2:B{n_row_loaded}"
        if os.path.exists(PATH_LOG):
            print(f"found downloaded file {PATH_LOG} ")
            print(f"clearing player log {range_name}...")
            sheet_clear(service, spreadsheet_id, sheet_name, range_name)
    
    else:
        print('player log is empty !')

    print("sync shuttlecock...")
    sheet_name = "shuttlecock_log"
    range_name = "A1:D50"
    sheet_shuttlecock, list_shuttlecock = sheet_read(service, spreadsheet_id, sheet_name, range_name)

    if len(list_shuttlecock) > 1:
        timestamp_log = list_shuttlecock[-1][0]
        timestamp_log = change_format_ts(timestamp_log, is_datetime=True)
        filename_gg = f'{timestamp_log}_shuttlecock_ggsheet.csv'
        PATH_LOG = os.path.join(FOLDER_PROJECT, 'data', 'cloud', 'shuttlecock', filename_gg)
        if not os.path.exists(PATH_LOG):
            mylib.list2csv(PATH_LOG, list_shuttlecock, is_nested_list=True)
            FOLDER_SAVE = pjoin(FOLDER_PROJECT, 'record', 'shuttlecock', 'ggsheet')
            if not os.path.exists(FOLDER_SAVE):
                os.makedirs(FOLDER_SAVE)
            write_logday(list_shuttlecock, FOLDER_SAVE, 'shuttlecock')

        else:
            print("shuttlecock log already up to date.")

        sheet_name = "shuttlecock_log"
        n_row_loaded = len(list_shuttlecock)
        range_name = f"A2:D{n_row_loaded}"
        if os.path.exists(PATH_LOG):
            print(f"found downloaded file {PATH_LOG} ")
            print(f"clearing shuttlecock_log {range_name}...")
            sheet_clear(service, spreadsheet_id, sheet_name, range_name)
    
    else:
        print('shuttlecock log is empty !')
   
    print(f"[Done] {sys.argv[0]}")