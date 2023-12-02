import os
from os.path import join as pjoin
import sys
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

import lib as wedolib


# load logday player
FOLDER_LOGDAY = pjoin(FOLDER_PROJECT, 'record', 'player', 'ggsheet')
list_dir, list_folder, list_name = wedolib.findFile(FOLDER_LOGDAY, '*.csv', 0)


for i, path_logday_player in enumerate(list_dir):
    print(f'{i} {path_logday_player}')
    filename = list_name[i]
    log_date = filename.split('_')[0]

    df_player = pd.read_csv(path_logday_player)
    
    # load logday shuttlecock
    filename_shuttle = f'{log_date}_logday_shuttlecock.csv'
    PATH_SHUTTLECOCK = pjoin(FOLDER_PROJECT, 'record', 'shuttlecock', filename_shuttle)
    df_shuttlecock = pd.read_csv(PATH_SHUTTLECOCK)

    df_listplayer = pd.concat([df_player, df_shuttlecock], axis=1)

    pass

