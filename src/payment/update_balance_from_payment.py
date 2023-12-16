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
if n_files > 0:
    for ifile in range(n_files):
        filename = list_name[ifile]
        path_file = list_dir[ifile]
        df_pay = pd.read_csv(path_file)

        n_user = df_pay.shape[0]
        print(f'updating balance from payment {filename}')
        for i in range(n_user):
            name_from_form = df_pay['name'][i]
            player_code = df_user_code.loc[name_from_form, 'player_code']
            player_team = df_user_code.loc[name_from_form, 'team']
            player_name = df_user_code.loc[name_from_form, 'name']

            player_pay = df_pay['payment'][i]
            timestamp_pay = df_pay['timestamp'][i]
            balance_prev = df_balance.loc[player_code, 'balance']
            balance_current = balance_prev + player_pay 
            df_balance.loc[player_code, 'balance'] = balance_current

            # update player history
            filename_player_balance = f'balance_{player_team}_{player_name}.csv'
            FOLDER_ACCOUNT_PLAYER = os.path.join(FOLDER_PROJECT, 'account', 'by_player', player_team)
            if not os.path.exists(FOLDER_ACCOUNT_PLAYER):
                os.makedirs(FOLDER_ACCOUNT_PLAYER)
            PATH_ACCOUNT_PLAYER = os.path.join(FOLDER_ACCOUNT_PLAYER, filename_player_balance)
            # PATH_ACCOUNT_PLAYER_ONEDRIVE = os.path.join(FOLDER_BADMINTON_ONEDRIVE, 'account', 'by_player', filename_player_balance)
            dictHist = {
                "date": timestamp_pay,
                "team": player_team,
                "player_name": player_name,
                "player_code": player_code,
                "price_per_player": 0,
                "n_player_come": 0,
                "balance_prev": balance_prev,
                "bill": 0,
                "payment": player_pay,
                "balance": balance_current
            }
            dfBalancePlayerHistNew = pd.DataFrame(dictHist, index=[0])
            if os.path.exists(PATH_ACCOUNT_PLAYER):
                # load and append
                dfBalancePlayerHist = pd.read_csv(PATH_ACCOUNT_PLAYER, index_col=False)
                # dfBalancePlayerHist = dfBalancePlayerHist.append(dfBalancePlayerHistNew)
                dfBalancePlayerHist = pd.concat([dfBalancePlayerHist, dfBalancePlayerHistNew], ignore_index=True)
                dfBalancePlayerHist.to_csv(PATH_ACCOUNT_PLAYER, index=False)

            else:
                # create new 
                dfBalancePlayerHistNew.to_csv(PATH_ACCOUNT_PLAYER, index=False)

    df_balance.reset_index(inplace=True)
    df_balance.to_csv(path_balance, index=False)

    for ifile in range(n_files):
        path_ori = list_dir[ifile]
        filename = list_name[ifile]

        path_new = pjoin(FOLDER_PROJECT, 'data', 'checked', 'payment', filename)
        if os.path.exists(path_new):
            print(f'deleting {path_ori}...')
            os.remove(path_ori)
            
        else:
            print(f'moving {path_new}')
            os.rename(path_ori, path_new)

print("#----- Finish update balance -----#")