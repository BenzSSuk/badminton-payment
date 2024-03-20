import os
from datetime import datetime

def change_format_ts(timestamp, is_datetime=True, file_type="ggsheet"):
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