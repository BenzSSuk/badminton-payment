import os
from os.path import join as pjoin
import sys
import pandas as pd
import numpy as np
import math

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
FOLDER_DATA = pjoin(FOLDER_PROJECT, 'data')

import lib as wedolib

FOLDER_PLAYER_RAW = pjoin(FOLDER_DATA, 'ggsheet', 'landing', 'player')
FOLDER_PLAYER_RAW_KEEP = pjoin(FOLDER_DATA, 'ggsheet', 'checked', 'player')
wedolib.isFolderExist(FOLDER_PLAYER_RAW_KEEP)
FOLDER_PLAYER_DAY = pjoin(FOLDER_DATA, 'split_day', 'player')
wedolib.isFolderExist(FOLDER_PLAYER_DAY)

FOLDER_SHUTTLECOCK_RAW = pjoin(FOLDER_DATA, 'ggsheet', 'landing', 'shuttlecock')
FOLDER_SHUTTLECOCK_RAW_KEEP = pjoin(FOLDER_DATA, 'ggsheet', 'checked', 'shuttlecock')
wedolib.isFolderExist(FOLDER_SHUTTLECOCK_RAW_KEEP)
FOLDER_SHUTTLECOCK_DAY = pjoin(FOLDER_DATA, 'split_day', 'shuttlecock')
wedolib.isFolderExist(FOLDER_SHUTTLECOCK_DAY)

def split_day_log_and_save(folder_file_raw, folder_file_day, suffix='player', folder_checked=None):
    # load logday player
    list_dir, list_folder, list_name = wedolib.findFile(folder_file_raw, '*.csv', 0)
    if len(list_name) == 0:
        print(f"folder {folder_file_raw} is empty !")
        return

    for i, path_player_raw in enumerate(list_dir):
        filename = list_name[i]
        log_date = filename.split('_')[0]

        df_player_raw = pd.read_csv(path_player_raw)
        # df_player_raw_reindex = df_player_raw.set_index('timestamp')

        list_day = df_player_raw['timestamp'].unique()

        for log_day in list_day:
            print(f"{filename} {log_day}...")
            df_player_day = df_player_raw[df_player_raw['timestamp']==log_day]

            log_day_reformat = log_day.split(' ')[0]
            log_day_reformat = log_day_reformat.replace("-", "")

            year = log_day_reformat[0:4]
            mm = log_day_reformat[4:6]
            dd = log_day_reformat[6:8]

            filename_log_day = f'{log_day_reformat}_logday_{suffix}.csv'
            folder_player_day = pjoin(folder_file_day, year)
            wedolib.isFolderExist(folder_player_day)
            path_player_day = pjoin(folder_player_day, filename_log_day)
            df_player_day.to_csv(path_player_day, index=False)

        os.rename(pjoin(folder_file_raw, filename), pjoin(folder_checked, filename))

split_day_log_and_save(FOLDER_PLAYER_RAW, FOLDER_PLAYER_DAY, 'player', FOLDER_PLAYER_RAW_KEEP)
split_day_log_and_save(FOLDER_SHUTTLECOCK_RAW, FOLDER_SHUTTLECOCK_DAY, 'shuttlecock', FOLDER_SHUTTLECOCK_RAW_KEEP)
