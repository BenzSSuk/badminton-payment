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
FOLDER_DATA = pjoin(FOLDER_PROJECT, 'data')
FOLDER_ACCOUNT = pjoin(FOLDER_PROJECT, 'account')

import lib.DataProcessing as mylib

folder_acc_player = pjoin(FOLDER_ACCOUNT, 'by_player')

list_dir, list_folder, list_filename = mylib.findFile(folder_acc_player, '*.csv', -1)

n_file = len(list_filename)

dict_lasted_balance = {}
for i in range(n_file):
    path_file = list_dir[i]
    filename = list_filename[i]

    # get name and team
    split_buff = filename.split('_')
    player_team = split_buff[1]
    player_name = split_buff[-1].split('.')[0]

    print(f'{player_team} {player_name}')
    df_player_acc = pd.read_csv(path_file)

    dict_lasted_balance = mylib.addFeatureToDict(dict_lasted_balance, 'team', player_team)
    dict_lasted_balance = mylib.addFeatureToDict(dict_lasted_balance, 'name', player_name)
    dict_lasted_balance = mylib.addFeatureToDict(dict_lasted_balance, 'balance', df_player_acc.iloc[-1]['balance'])

df_lasted_balance = pd.DataFrame(dict_lasted_balance)
folder_save = pjoin(FOLDER_PROJECT, 'account')
mylib.isFolderExist(folder_save)
filename_save = f'player_lasted_balance.csv'
path_filesave = pjoin(folder_save, filename_save)
df_lasted_balance.to_csv(path_filesave, index=False)