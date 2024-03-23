from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime
import pandas as pd

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

    def read(self, sheet_name, range, output_type='df'):
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
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=range_name)
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
  
    def write_data(self, df_data, PATH_FILE):
        is_write_successed = False

        df_data.to_csv(PATH_FILE, index=False)

        # checking write file
        df_data_write = pd.read_csv(PATH_FILE)

        is_write_successed = df_data.shape == df_data_write.shape

        return is_write_successed

    def clear(self, sheet_name, range):
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
                self.service.spreadsheets()
                .values()
                .clear(spreadsheetId=self.spreadsheet_id, range=range_name)
                .execute()
            )
            # rows = result.get("values", [])
            # print(f"{len(rows)} rows retrieved")

            # list_value = result['values']

            # return result, list_value
        
        except HttpError as error:
            print(f"An error occurred: {error}")

            return error
  

    def delete(self, sheet_id, index_axis='', range=[0, 0]):
        '''
        input:
            sheet_id :
                example https://docs.google.com/spreadsheets/d/WrdsqdgvWE/edit#gid=1512194892

                                    spreadsheet_id='WrdsqdgvWE'  sheet_id='1512194892''
            
            index_axis : 'ROWS' or 'COLUMNS' 
            range : [startIndex, endIndex]
        '''
        if not index_axis in ['ROWS', 'COLUMNS']:
            raise ValueError(f'index_axis = ROWS or COLUMNS')
        
        # Create the request body
        list_request_body = [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": index_axis,
                        "startIndex": range[0],
                        "endIndex": range[1]
                    }
                }
            }
        ]
        # list_request_body = [
        #     {
        #     "deleteDimension": {
        #         "range": {
        #         "sheetId": sheet_name,
        #         "dimension": "ROWS",
        #         "startIndex": 0,
        #         "endIndex": 3
        #         }
        #     }
        #     },
        #     {
        #     "deleteDimension": {
        #         "range": {
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
        #     "responseRanges": [""],
        #     "responseIncludeGridData": False    
        # }

        # Execute the batch update
        request = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                     body=sheet_request_body)
        request.execute()

    def delete_row_data(self, sheet_id, n_row):
        # n_row = df_data.shape[0]
        self.delete(sheet_id, 'ROWS', [1, n_row + 1])

    def close(self):
        self.service.close()
