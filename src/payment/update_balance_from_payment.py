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
FOLDER_DATA = pjoin(FOLDER_PROJECT, 'data')
FOLDER_GGSHEET = pjoin(FOLDER_DATA, 'ggsheet')

import lib.DataProcessing as mylib

PATH_USER_CODE = pjoin(FOLDER_PROJECT, 'data', 'user_id', 'user_code.csv')
df_user_code = pd.read_csv(PATH_USER_CODE)
df_user_code.set_index('name_on_form', inplace=True)

# update with payment from google form
FOLDER_PAY = pjoin(FOLDER_GGSHEET, 'landing', 'payment')
list_dir, list_folder, list_name = mylib.findFile(FOLDER_PAY, '*.csv', 0)
n_files = len(list_name)
if n_files > 0:
    for ifile in range(n_files):
        filename = list_name[ifile]
        path_file_player_pay = list_dir[ifile]

        # check is already update this file
        folder_checked = pjoin(FOLDER_GGSHEET, 'checked', 'payment')
        path_file_player_pay_checked = pjoin(folder_checked, filename)
        if os.path.exists(path_file_player_pay_checked):
            # already checked this file
            continue

        df_pay = pd.read_csv(path_file_player_pay)
        df_pay.columns = ['timestamp', 'path_slip', 'payment', 'name']

        n_user = df_pay.shape[0]
        
        for i in range(n_user):
            name_from_form = df_pay['name'][i]
            player_pay = df_pay['payment'][i]
            timestamp_pay = df_pay['timestamp'][i]

            player_code = df_user_code.loc[name_from_form, 'player_code']
            player_team = df_user_code.loc[name_from_form, 'team']
            player_name = df_user_code.loc[name_from_form, 'name']

            print(f'updating payment {timestamp_pay} {player_code} {player_pay} bath')

            # load account
            filename_account_player = f'balance_{player_team}_{player_name}.csv'
            folder_account_player = pjoin(FOLDER_PROJECT, 'account', 'by_player', player_team)
            path_account_player = pjoin(folder_account_player, filename_account_player)
            dfBalancePlayerHist = pd.read_csv(path_account_player, index_col=False)
            
            # check is already update this transaction or not
            if timestamp_pay in dfBalancePlayerHist['date'].to_list():
                print(f'found this transaction {timestamp_pay} in player histrory, skipping...')
                continue
            
            # calculate balance
            balance_prev = dfBalancePlayerHist['balance'].iloc[-1]
            balance_current = balance_prev + player_pay
            
            # update player history
            filename_player_balance = f'balance_{player_team}_{player_name}.csv'
            FOLDER_ACCOUNT_PLAYER = os.path.join(FOLDER_PROJECT, 'account', 'by_player', player_team)
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
                dfBalancePlayerHistUpdate = pd.concat([dfBalancePlayerHist, dfBalancePlayerHistNew], ignore_index=True)
                dfBalancePlayerHistUpdate.to_csv(PATH_ACCOUNT_PLAYER, index=False)

            else:
                if not os.path.exists(FOLDER_ACCOUNT_PLAYER):
                    os.makedirs(FOLDER_ACCOUNT_PLAYER)
                # create new 
                print(f'create new account player {filename_player_balance}...')
                dfBalancePlayerHistNew.to_csv(PATH_ACCOUNT_PLAYER, index=False)

        # move file to checked
        print(f'moving {path_file_player_pay} to {path_file_player_pay_checked}...')
        mylib.isFolderExist(folder_checked)
        os.rename(path_file_player_pay, path_file_player_pay_checked)

print(f"[Done] {sys.argv[0]}")