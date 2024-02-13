import os
from os.path import join as pjoin
import sys
import math
import pandas as pd
import subprocess

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

import lib.DataProcessing as wedolib

FOLDER_RECORD = pjoin(FOLDER_PROJECT, 'record')
FOLDER_CHECKED = pjoin(FOLDER_PROJECT, 'data', 'checked')

FOLDER_PLAYER_CHECKED = pjoin(FOLDER_CHECKED, 'player')
_, _, list_name_checked = wedolib.findFile(FOLDER_PLAYER_CHECKED, '*.xlsx', 0)

# check log player record
print('checking player...')
FOLDER_LOGTYPE = 'player'
FOLDER_PLAYER_SHEET = pjoin(FOLDER_RECORD, FOLDER_LOGTYPE, 'ggsheet')
list_dir_ggsheet, _, list_name_ggsheet = wedolib.findFile(FOLDER_PLAYER_SHEET, '*.csv', 0)

for i, filename_ggsheet in enumerate(list_name_ggsheet):
    day_log = filename_ggsheet.split('_')[0]

    filename_player_checked_mock = f'{day_log}_listplayer.xlsx'
    if filename_player_checked_mock in list_name_checked:
        path_ori = list_dir_ggsheet[i]

        path_new = pjoin(FOLDER_CHECKED, f'{FOLDER_LOGTYPE}_cloud', filename_ggsheet)
        if os.path.exists(path_new):
            print(f'deleting {path_ori}...')
            os.remove(path_ori)
            
        else:
            print(f'moving {path_new}')
            os.rename(path_ori, path_new)

# check log shulltecock
print('checking shuttlecock...')
FOLDER_LOGTYPE = 'shuttlecock'
FOLDER_SHEET = pjoin(FOLDER_RECORD, FOLDER_LOGTYPE, 'ggsheet')
list_dir_ggsheet, _, list_name_ggsheet = wedolib.findFile(FOLDER_SHEET, '*.csv', 0)

for i, filename_ggsheet in enumerate(list_name_ggsheet):
    day_log = filename_ggsheet.split('_')[0]

    filename_player_checked_mock = f'{day_log}_listplayer.xlsx'
    if filename_player_checked_mock in list_name_checked:
        path_ori = list_dir_ggsheet[i]
        path_new = pjoin(FOLDER_CHECKED, FOLDER_LOGTYPE, filename_ggsheet)
        if os.path.exists(path_new):
            print(f'deleting {path_ori}...')
            os.remove(path_ori)
            
        else:
            print(f'moving {path_new}')
            os.rename(path_ori, path_new)

print(f"[Done] {sys.argv[0]}")
# # check log payment
# print('checking payment...')
# FOLDER_LOGTYPE = 'payment'
# FOLDER_SHEET = pjoin(FOLDER_RECORD, FOLDER_LOGTYPE, 'ggform')
# list_dir_ggsheet, _, list_name_ggsheet = wedolib.findFile(FOLDER_SHEET, '*.csv', 0)

# for i, filename_ggsheet in enumerate(list_name_ggsheet):
#     day_log = filename_ggsheet.split('_')[0]

#     filename_player_checked_mock = f'{day_log}_listplayer.xlsx'
#     if filename_player_checked_mock in list_name_checked:
#         path_ori = list_dir_ggsheet[i]
#         path_new = pjoin(FOLDER_CHECKED, FOLDER_LOGTYPE, filename_ggsheet)
#         if os.path.exists(path_new):
#             print(f'deleting {path_ori}...')
#             os.remove(path_ori)
            
#         else:
#             print(f'moving {path_new}')
#             os.rename(path_ori, path_new)