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

import lib as srisuk

if __name__ == "__main__":

    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("google authen...")
    creds = srisuk.google_authen(FOLDER_CONFIG)

    print("build google sheet service...")
    PATH_SHEET_ID = pjoin(FOLDER_CONFIG, 'ggsheet.json')
    dict_ggsheet_info = srisuk.read_json(PATH_SHEET_ID)

    filename_sheet = 'user_log'
    sheet_info = dict_ggsheet_info[filename_sheet]
    sheet = srisuk.SpreadSheet(creds=creds, spreadsheet_id=sheet_info['spreadsheet_id'])
    
    print("sync user id...")
    sheet_name = "userID"
    range_name = "A1:E300"
    df_user_id = sheet.read(sheet_name, range_name)
    PATH_USER_ID = os.path.join(FOLDER_DATA, 'user_id', 'user_id_rf.csv')
    sheet.write_data(df_user_id, PATH_USER_ID)

    print("sync player log...")
    sheet_name = "log"
    range_name = "A1:B300"
    df_player_log = sheet.read(sheet_name, range_name)

    # if len(list_data_row_player) > 1:
    if not df_player_log.empty:
        timestamp_log = df_player_log['timestamp'].iloc[-1]
        timestamp_log = srisuk.change_format_ts(timestamp_log, 'ggsheet')
        
        filename_gg = f'{timestamp_log}_log_ggsheet.csv'
        PATH_LOG = os.path.join(FOLDER_PROJECT, 'record', 'player', 'ggsheet', filename_gg)
        
        is_write_successed = sheet.write_data(df_player_log, PATH_LOG)
        
        if is_write_successed:
            print('write file player log successed, deleting...')
            n_row = df_player_log.shape[0]
            sheet.delete_row_data(sheet_info['sheet_id'][sheet_name], n_row)
        else:
            print('write file player log fail !')

    else:
        print('player log is empty !')

    print("sync shuttlecock...")
    sheet_name = "shuttlecock_log"
    range_name = "A1:D50"
    df_shuttlecock = sheet.read(sheet_name, range_name)

    if not df_shuttlecock.empty:
        timestamp_log = df_shuttlecock['timestamp'].iloc[-1]
        timestamp_log = srisuk.change_format_ts(timestamp_log, is_datetime=True)
        filename_gg = f'{timestamp_log}_shuttlecock_ggsheet.csv'
        PATH_LOG = os.path.join(FOLDER_PROJECT, 'record', 'shuttlecock', 'ggsheet', filename_gg)
        
        is_write_successed = sheet.write_data(df_shuttlecock, PATH_LOG)
        if is_write_successed:
            print("write shuttlecock successed, deleting...")
            n_row = df_shuttlecock.shape[0]
            sheet.delete_row_data(sheet_info['sheet_id'][sheet_name], n_row)

        else:
            print("write shuttlecock fail !")

    else:
        print('shuttlecock log is empty !')
   
    print(f"[Done] {sys.argv[0]}")