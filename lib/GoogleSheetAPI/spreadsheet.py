from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime
import pandas as pd
import os, sys
from os.path import join as pjoin

def checkSysPathAndAppend(path, stepBack=0):
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
FOLDER_DATA = os.path.join(FOLDER_PROJECT, 'data')

import lib as mylib

class SpreadSheet:
    def __init__(self, creds, spreadsheet_id='', gservice="sheets", version='v4'):
        self.service = build(gservice, version, credentials=creds)
        self.set_spreadsheet_id(spreadsheet_id)
    
    def set_spreadsheet_id(self, spreadsheet_id):
        ''' 
            example https://docs.google.com/spreadsheets/d/WrdsqdgvWE/edit#gid=1512194892

                                spreadsheet_id='WrdsqdgvWE'  sheet_id='1512194892''
        '''
        self.spreadsheet_id = spreadsheet_id

    # def set_sheet_id(self, sheet_id):
    #     self.sheet_id = sheet_id

    def read(self, sheet_name, sheet_range, output_type='df'):
        """
        Creates the batch_update the user has access to.
        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """

        # creds, _ = google.auth.default()
        
        # pylint: disable=maybe-no-member
        try:
            sheet_range_name = f"{sheet_name}!{sheet_range}"
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=sheet_range_name)
                .execute()
            )
            # rows = result.get("values", [])
            # print(f"{len(rows)} rows retrieved")

            list_value = result['values']
            if output_type == 'df':
                # header = list_value[0]
                header = list_value[0]
                list_value.remove(list_value[0])
                data = list_value
                df_data = pd.DataFrame(data, columns=header)
                df_data.reset_index(drop=True, inplace=True)

                return df_data
            
            else:
                return list_value
        
        except HttpError as error:
            print(f"An error occurred: {error}")

            return error

    def get_filename_timestamp(self, df_data, header, filename, format_ts='%Y-%m-%d %H%M%S'):
        n_row = df_data.shape[0]
        timestamp_str = df_data.loc[n_row-1, header]
        timestamp_str_new = mylib.change_timestamp_format(timestamp_str, format_ts, "%Y%m%d_%H%M%S")
        filename_timestamp = f'{timestamp_str_new}_{filename}'

        return filename_timestamp

    def write_data(self, df_data, path_file):
        if df_data.empty:
            return False

        # path_file = pjoin(folder_file, filename)
        df_data.to_csv(path_file, index=False)
        df_data_write = pd.read_csv(path_file)

        is_write_successed = (df_data.shape == df_data_write.shape)

        return is_write_successed
    
    def read_and_write(self, sheet_name, sheet_range, folder_file, filename,
                       header_timestamp=None, format_ts=None):
        df_data = self.read(sheet_name, sheet_range, output_type='df')
        if df_data.empty:
            return False

        if header_timestamp:
            filename_ts = self.get_filename_timestamp(df_data, header_timestamp, filename, format_ts=format_ts)
        else:
            filename_ts = filename
        path_file = pjoin(folder_file, filename_ts)

        return self.write_data(df_data, path_file)

    def clear(self, sheet_name, sheet_range):
        """
        Creates the batch_update the user has access to.
        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """

        # creds, _ = google.auth.default()
        # pylint: disable=maybe-no-member
        try:
            sheet_range_name = f"{sheet_name}!{sheet_range}"
            result = (
                self.service.spreadsheets()
                .values()
                .clear(spreadsheetId=self.spreadsheet_id, sheet_range=sheet_range_name)
                .execute()
            )
            # rows = result.get("values", [])
            # print(f"{len(rows)} rows retrieved")
            # list_value = result['values']
            # return result, list_value
        
        except HttpError as error:
            print(f"An error occurred: {error}")

            return error

    def delete(self, sheet_id, index_axis='', sheet_range=[0, 0]):
        '''
        input:
            sheet_id :
                example https://docs.google.com/spreadsheets/d/WrdsqdgvWE/edit#gid=1512194892

                                    spreadsheet_id='WrdsqdgvWE'  sheet_id='1512194892''
            
            index_axis : 'ROWS' or 'COLUMNS' 
            sheet_range : [startIndex, endIndex]
        '''
        list_index_axis = ['ROWS', 'COLUMNS']
        if not index_axis in list_index_axis:
            raise ValueError(f'index_axis must be one of {list_index_axis}')
        
        # Create the request body
        list_request_body = [
            {
                "deleteDimension": {
                    "sheet_range": {
                        "sheetId": sheet_id,
                        "dimension": index_axis,
                        "startIndex": sheet_range[0],
                        "endIndex": sheet_range[1]
                    }
                }
            }
        ]
        # list_request_body = [
        #     {
        #     "deleteDimension": {
        #         "sheet_range": {
        #         "sheetId": sheet_name,
        #         "dimension": "ROWS",
        #         "startIndex": 0,
        #         "endIndex": 3
        #         }
        #     }
        #     },
        #     {
        #     "deleteDimension": {
        #         "sheet_range": {
        #         "sheetId": sheet_name,
        #         "dimension": "COLUMNS",
        #         "startIndex": 1,
        #         "endIndex": 4
        #         }
        #     }
        #     },
        # ],

        sheet_request_body = {
            "requests": list_request_body,
            "includeSpreadsheetInResponse": False,
        }
        # update_spreadsheet_data = {
        #     "requests": spreadsheet_data,
        #     "includeSpreadsheetInResponse": False,
        #     "responsesheet_ranges": [""],
        #     "responseIncludeGridData": False    
        # }

        # Execute the batch update
        request = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                     body=sheet_request_body)
        request.execute()

    def delete_first_n_row(self, sheet_id, n_row, skip_row=0):
        sheet_range = [0+skip_row, n_row+skip_row]
        self.delete(sheet_id, index_axis='ROWS', sheet_range=sheet_range)

    def delete_first_n_col(self, sheet_id, n_col, skip_col=0):
        sheet_range = [0+skip_col, n_col+skip_col]
        self.delete(sheet_id, index_axis='COLUMNS', sheet_range=sheet_range)

    def close(self):
        self.service.close()
