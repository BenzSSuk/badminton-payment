import os
from os.path import join as pjoin
import sys
import pandas as pd
import subprocess

from os.path import join as pjoin

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

# load current balance
path_balance = pjoin(FOLDER_PROJECT, 'account', 'wedo_badminton_balance.csv')
df_balance = pd.read_csv(path_balance)
df_balance.set_index('player_code', inplace=True)

PATH_USER_CODE = pjoin(FOLDER_PROJECT, 'data', 'user_id', 'user_code.csv')
df_user_code = pd.read_csv(PATH_USER_CODE)
df_user_code.set_index('name_on_form', inplace=True)

# update with payment from google form
FOLDER_PAY = pjoin(FOLDER_PROJECT, 'record', 'payment', 'ggform')
list_dir, list_folder, list_name = wedolib.findFile(FOLDER_PAY, '*.csv', 0)
n_files = len(list_name)
for ifile in range(n_files):
    filename = list_name[ifile]
    path_file = list_dir[ifile]
    df_pay = pd.read_csv(path_file)

    n_user = df_pay.shape[0]
    print(f'updating balance from payment {filename}')
    for i in range(n_user):
        name_from_form = df_pay['name'][i]
        player_code = df_user_code.loc[name_from_form, 'player_code']

        player_pay = df_pay['payment'][i]
        df_balance.loc[player_code, 'balance'] = df_balance.loc[player_code, 'balance'] + player_pay


df_balance.reset_index(inplace=True)
df_balance.to_csv(path_balance, index=False)

for ifile in range(n_files):
    path_file = list_dir[ifile]
    filename = list_name[ifile]

    path_file_new = pjoin(FOLDER_PROJECT, 'data', 'checked', 'payment', filename)
    os.rename(path_file, path_file_new)

print("#----- Finish update balance -----#")