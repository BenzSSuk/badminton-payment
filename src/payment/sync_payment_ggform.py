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

dict_format_timestamp = {
    "ggsheet": {
        "date": "%Y-%m-%d",
        "datetime": "%Y-%m-%d %H:%M"
    },
    "ggform": {
        "date": "%d/%m/%Y",
        "datetime": "%d/%m/%Y, %H:%M:%S"
    }
}

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

def sheet_delete_row_col(service, spreadsheet_id, sheet_name, range):
    new_spreadsheet_data = {
        "requests": [
            {
            "deleteDimension": {
                "range": {
                "sheetId": sheet_name,
                "dimension": "ROWS",
                "startIndex": 0,
                "endIndex": 3
                }
            }
            },
            {
            "deleteDimension": {
                "range": {
                "sheetId": sheet_name,
                "dimension": "COLUMNS",
                "startIndex": 1,
                "endIndex": 4
                }
            }
            },
        ],
    }
    
    result = (
        service.spreadsheets()
        .batch_update(spreadsheetId=spreadsheet_id, body=new_spreadsheet_data)
        .execute()
    )
        
    # sheet_service.spreadsheets().batchUpdate(
    #     spreadsheetId=spreadsheet_id, body=update_data)

def change_format_ts(timestamp, is_datetime=True, file_type="ggsheet"):


    if is_datetime:
        timestamp_datetime = datetime.strptime(timestamp, dict_format_timestamp[file_type]["datetime"])
        timestamp_new = timestamp_datetime.strftime("%Y%m%d_%H%M%S")
    
    else:
        timestamp_datetime = datetime.strptime(timestamp, dict_format_timestamp[file_type]["date"])
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
  
    creds = mylib.get_credentials(FOLDER_CONFIG, SCOPES=SCOPES, method='service_account', filename_json_key='admin01.json')

    print("build google sheet service...")
    service = build("sheets", "v4", credentials=creds)
    
    # print("read data from sheet...")
    spreadsheet_id = "1645HEPOmEV723MY27-sttmxb6_dT6YK0EJyUvocvbOE"

    print("sync player payment...")
    sheet_name = "payment"
    range_name = "A1:D300"
    sheet_log, list_data_row = sheet_read(service, spreadsheet_id, sheet_name, range_name)
    
    if len(list_data_row) > 1:
        timestamp_log = list_data_row[-1][0]
        timestamp_log = change_format_ts(timestamp_log, is_datetime=True, file_type="ggform")

        filename_gg = f'{timestamp_log}_payment_ggform.csv'
        FOLDER_LOG = pjoin(FOLDER_PROJECT, 'record', 'payment', 'ggform')
        if not os.path.exists(FOLDER_LOG):
            os.makedirs(FOLDER_LOG)
        PATH_LOG = os.path.join(FOLDER_LOG, filename_gg)
        # PATH_LOG_CHECKED = pjoin(FOLDER_PROJECT, 'data', 'checked', 'payment', filename_gg)
        # if os.path.exists(PATH_LOG) or os.path.exists(PATH_LOG_CHECKED):
        # if os.path.exists(PATH_LOG):
        #     print("payment log already up to date.")

        # else:
        print("writing log payment...")
        list_data_row[0] = ['timestamp', 'img_slip', 'payment', 'name']
        mylib.list2csv(PATH_LOG, list_data_row, is_nested_list=True)
        # write_logday(list_data_row, 'player', 'logday_player.csv')

        sheet_name = "payment"
        n_row_loaded = len(list_data_row)
        range_name = f"A2:D{n_row_loaded}"
        # if os.path.exists(PATH_LOG) or os.path.exists(PATH_LOG_CHECKED):
        if os.path.exists(PATH_LOG):
            print(f"found downloaded file {PATH_LOG} ")
            print(f"clearing player log {range_name}...")
            sheet_clear(service, spreadsheet_id, sheet_name, range_name)
    
    else:
        print('payment log is empty !')
    
    print(f"[Done] {sys.argv[0]}")