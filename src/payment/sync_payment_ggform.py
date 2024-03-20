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

import lib.DataProcessing as mylib
import lib as srisuk

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

if __name__ == "__main__":
  
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("google authen...")
    creds = google_authen(FOLDER_CONFIG)

    print("build google sheet service...")
    PATH_SHEET_ID = pjoin(FOLDER_CONFIG, 'ggsheet.json')
    dict_ggsheet_info = srisuk.read_json(PATH_SHEET_ID)

    filename_sheet = 'payment'
    sheet_info = dict_ggsheet_info[filename_sheet]
    sheet = srisuk.SpreadSheet(creds=creds, spreadsheet_id=sheet_info['spreadsheet_id'])
    
    print("reading...")
    df_data = sheet.read('payment', 'a1:d200')
    if not df_data.empty():
        df_data.columns = ['timestamp', 'img_slip', 'payment', 'name']

        print("writing...")
        timestamp_log = df_data['timestamp'].iloc[-1]
        timestamp_log = srisuk.change_format_ts(timestamp_log, is_datetime=True, file_type="ggform")

        filename_gg = f'{timestamp_log}_payment_ggform.csv'
        FOLDER_LOG = pjoin(FOLDER_PROJECT, 'record', 'payment', 'ggform')
        if not os.path.exists(FOLDER_LOG):
            os.makedirs(FOLDER_LOG)
        PATH_LOG = os.path.join(FOLDER_LOG, filename_gg)
        is_write_successed = sheet.write_data(df_data, PATH_FILE=PATH_LOG)
        
        if is_write_successed:
            print('deleting...')
            nrow, ncol = df_data.shape
            sheet.delete(sheet_info['sheet_id']['payment'], index_axis='ROWS', range=[1, nrow + 1])
            print('delete succeedful !')

        else:
            print('Writing not completed, not delete !')

    else:
        print('Sheet is empty !')
        
    sheet.close()
    
    print(f"[Done] {sys.argv[0]}")