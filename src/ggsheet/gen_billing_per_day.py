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
FOLDER_RECORD_EXCEL = pjoin(FOLDER_PROJECT, 'record', 'player', 'excel')
if not os.path.exists(FOLDER_RECORD_EXCEL):
    os.makedirs(FOLDER_RECORD_EXCEL)

import lib as wedolib

def get_df_listplayer(df_listplayer):
    # ---------- add column is_play, billing, payment ----------
    df_listplayer['is_play'] = np.ones((n_row, 1))
    df_listplayer['bill'] = np.zeros((n_row, 1))
    df_listplayer['payment'] = np.zeros((n_row, 1))

    # ---------- add shuttlecock info ----------
    # load logday shuttlecock
    dict_shuttlecock = {
        "price_shuttle": 0,
        "n_shuttle": 0,
        "external_pay": 0,
        "pay_to_external": 0,
        "total": 0,
        "price_per_player": 0 
    }
    df_shuttlecock = pd.DataFrame(dict_shuttlecock, index=[0])
    df_listplayer = pd.concat([df_listplayer, df_shuttlecock], axis=1)

    return df_listplayer

PATH_SHUTTLECOCK_BUY = os.path.join(FOLDER_PROJECT, 'data', 'purchase', 'shuttlecock_purchase.xlsx')
df_price_shuttlecock = pd.read_excel(PATH_SHUTTLECOCK_BUY)
shuttlecock_price_current = df_price_shuttlecock.iloc[-1]['price_single']

# load logday player
FOLDER_LOGDAY = pjoin(FOLDER_PROJECT, 'record', 'player', 'ggsheet')
list_dir, list_folder, list_name = wedolib.findFile(FOLDER_LOGDAY, '*.csv', 0)

for i, path_logday_player in enumerate(list_dir):
    filename = list_name[i]
    log_date = filename.split('_')[0]

    df_player = pd.read_csv(path_logday_player)
    n_row = df_player.shape[0]

    # preallocate df_listplayer template
    df_listplayer = get_df_listplayer(df_player.copy())

    # ---------- calculate billing ---------- 
    filename_shuttle = f'{log_date}_logday_shuttlecock.csv'
    PATH_SHUTTLECOCK = pjoin(FOLDER_PROJECT, 'record', 'shuttlecock', 'ggsheet', filename_shuttle)
    if os.path.exists(PATH_SHUTTLECOCK):
        print(f"calulating shuttlecock cost {log_date}...")
        df_shuttlecock_logday = pd.read_csv(PATH_SHUTTLECOCK)

        n_shuttlecock = df_shuttlecock_logday['n_shuttlecock'][0]
        external_pay = df_shuttlecock_logday['external_pay'][0]
        if math.isnan(external_pay):
            external_pay = 0
        # pay_to_external = df_shuttlecock_logday['pay_to_external'][0]
        total_cost = (shuttlecock_price_current * n_shuttlecock) - external_pay
        n_player = n_row
        price_per_player = np.ceil(total_cost/n_player)

        df_listplayer.loc[0, 'price_shuttle'] = shuttlecock_price_current
        df_listplayer.loc[0, 'n_shuttle'] = n_shuttlecock
        df_listplayer.loc[0, 'external_pay'] = external_pay
        # df_listplayer.loc[0, 'pay_to_external'] = 0
        df_listplayer.loc[0, 'total'] = total_cost
        df_listplayer.loc[0, 'n_player'] = n_player
        df_listplayer.loc[0, 'price_per_player'] = price_per_player

        df_listplayer['bill'] = price_per_player

    else:
        print(f'file logday {filename_shuttle} not found !')

    filename_excel = f'{log_date}_listplayer.xlsx'
    df_listplayer.to_excel(pjoin(FOLDER_RECORD_EXCEL, filename_excel), index=False)

print(f"[Done] {sys.argv[0]}")