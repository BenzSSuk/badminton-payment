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

'''
https://docs.google.com/spreadsheets/d/1QaZ5CNJCBPIRh6N95hoh1l4HOfZz8GjZR6vOKd7vU9s/edit?resourcekey#gid=1451979486
speardsheet_id = 1QaZ5CNJCBPIRh6N95hoh1l4HOfZz8GjZR6vOKd7vU9s
sheet_id = 1451979486
'''

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

# import lib.DataProcessing as mylib
import lib as mylib

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

if __name__ == "__main__":
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("google authen...")
    creds = mylib.get_credentials(FOLDER_CONFIG, SCOPES=SCOPES, method='service_account', filename_json_key='admin01.json')

    PATH_SHEET_ID = pjoin(FOLDER_CONFIG, 'ggsheet.json')
    dict_ggsheet_info = mylib.read_json(PATH_SHEET_ID)

    filename_spreadsheet = 'user_log'
    spreadsheet_info = dict_ggsheet_info[filename_spreadsheet]
    sheet = mylib.SpreadSheet(creds=creds, spreadsheet_id=spreadsheet_info['spreadsheet_id'])
    
    # print("reading...")
    # df_data = sheet.read(sheet_name='test', range='a1:d100', output_type='df')

    # print("writing...")
    # path_csv = pjoin(FOLDER_PROJECT, 'sheet_class_data.csv')
    # is_write_successed = sheet.write_data(df_data, PATH_FILE=path_csv)
    
    # if is_write_successed:
    #     print('deleting...')
    #     nrow, ncol = df_data.shape
    #     sheet.delete(spreadsheet_info['sheet_id']['test'], index_axis='ROWS', range=[1, nrow + 1])
    sheet.delete_first_n_row(spreadsheet_info['sheet_id']['test'], n_row=2, skip_row=1)


    sheet.close()

    print('Finished !')