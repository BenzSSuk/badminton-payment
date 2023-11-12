import os
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
FOLDER_PROJECT = checkSysPathAndAppend(folderFile, 0)

import lib.DataProcessing as wedolib

# update: update from current 
# rewrite: re write histroty from the first file 
MODE = "update" #
# FOLDER_BADMINTON_ONEDRIVE = os.path.join(r'C:\Users\Panna\OneDrive\Projects\badminton-payment')

# load daily player checklist
def initial_mode(MODE):
    if MODE == "update":
        folder_player_checker = os.path.join(FOLDER_PROJECT, 'player_rfid')

    elif MODE == "rewrite":
        folder_player_checker = os.path.join(FOLDER_PROJECT, 'player_rfid', 'checked')
        folder_account_date = os.path.join(FOLDER_PROJECT, 'account', 'by_date')
        list_dir, list_folder, list_file = wedolib.findFile(folder_account_date, '*.csv', 0)
        for path_delete in list_dir:
            os.remove(path_delete)

        folder_account_player = os.path.join(FOLDER_PROJECT, 'account', 'by_player')
        list_dir, list_folder, list_file = wedolib.findFile(folder_account_player, '*.csv', -1)
        for path_delete in list_dir:
            os.remove(path_delete)
    
    list_dir, list_folder, list_file = wedolib.findFile(folder_player_checker, '*.csv')
    list_dir.sort()
    list_folder.sort()
    list_file.sort()
    
    return list_dir, list_folder, list_file

def load_balance(FOLDER_PROJECT, ifile):
    # load balance
    if MODE == "update" or (MODE == "rewrite" and ifile > 0):
        path_lasted_balance = os.path.join(FOLDER_PROJECT, 'account', 'wedo_badminton_balance.csv')

    elif MODE == "rewrite":  
        path_lasted_balance = os.path.join(FOLDER_PROJECT, 'account', 'initial', 'account_balance_init.csv')

    dfBalance = pd.read_csv(path_lasted_balance)
    list_playercode_balance = list(dfBalance['player_code'].unique())
    dfBalancePlayer = dfBalance.copy()
    dfBalancePlayer['player_index'] = dfBalancePlayer['player_code']
    dfBalancePlayer.set_index('player_index', inplace=True)

    return dfBalancePlayer, list_playercode_balance

def get_n_and_price(dfPlayerCome):
    # list_playercode_come = list(dfPlayerCome['player_code'].unique())
    n_player = dfPlayerCome.shape[0]
    price_per_player = dfPlayerCome.iloc[0]['price_per_player']

    return n_player, price_per_player

list_dir, list_folder, list_file = initial_mode(MODE)
n_file = len(list_file)
if n_file > 0:
    # sort by date
    for ifile in range(n_file):
        filename_listplayer = list_file[ifile]
        date_log = filename_listplayer.split('_')[0]

        dfBalancePlayer, list_playercode_balance = load_balance(FOLDER_PROJECT, ifile)

        # player come
        folder_file = list_folder[ifile]
        path_file_listplayer = list_dir[ifile]
        # dfPlayerCome = pd.read_excel(path_file_listplayer)
        dfPlayerCome = pd.read_csv(path_file_listplayer)

        n_player, price_per_player = get_n_and_price(dfPlayerCome)

        dictNewPlayer = {
            'team': [],
            'player_name': [],
            'player_code': [],
            'balance': []
        }
        for iplayer in range(n_player):
            is_play = dfPlayerCome.iloc[iplayer]['is_play']
            player_team = dfPlayerCome.iloc[iplayer]['team']
            player_name = dfPlayerCome.iloc[iplayer]['player_name']
            player_code = dfPlayerCome.iloc[iplayer]['player_code']
            player_bill = dfPlayerCome.iloc[iplayer]['bill']
            player_pay = dfPlayerCome.iloc[iplayer]['payment']

            # hot fix
            # if player_code == 'TalayResource':
            #     player_code = 'TalayOM'
            #     player_team = 'OM'

            print(f'day {ifile+1}/{n_file}  player {iplayer+1}/{n_player} {date_log} {player_code}')

            if player_code in list_playercode_balance:
                # update balanceb
                balance_prev = dfBalancePlayer.loc[player_code, 'balance']
                balance_current = balance_prev - player_bill + player_pay
                dfBalancePlayer.loc[player_code, 'balance'] = balance_current

            else:
                # add new player, assume balance = 0
                balance_prev = 0
                balance_current = balance_prev - player_bill + player_pay

                dictNewPlayer['team'].append(player_team)
                dictNewPlayer['player_name'].append(player_name)
                dictNewPlayer['player_code'].append(player_code)
                dictNewPlayer['balance'].append(balance_current)

            # update player history
            filename_player_balance = f'balance_{player_team}_{player_name}.csv'
            FOLDER_ACCOUNT_PLAYER = os.path.join(FOLDER_PROJECT, 'account', 'by_player', player_team)
            if not os.path.exists(FOLDER_ACCOUNT_PLAYER):
                os.makedirs(FOLDER_ACCOUNT_PLAYER)
            PATH_ACCOUNT_PLAYER = os.path.join(FOLDER_ACCOUNT_PLAYER, filename_player_balance)
            # PATH_ACCOUNT_PLAYER_ONEDRIVE = os.path.join(FOLDER_BADMINTON_ONEDRIVE, 'account', 'by_player', filename_player_balance)
            dictHist = {
                "date": date_log,
                "team": player_team,
                "player_name": player_name,
                "player_code": player_code,
                "price_per_player": price_per_player,
                "n_player_come": is_play,
                "balance_prev": balance_prev,
                "bill": player_bill,
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
    

        # add new player
        dfNewPlayer = pd.DataFrame(dictNewPlayer)
        # dfBalancePlayerWrite = dfBalancePlayer.append(dfNewPlayer, ignore_index=True)
        dfBalancePlayerWrite = pd.concat([dfBalancePlayer, dfNewPlayer], ignore_index=True)

        # write balance date
        filename_balance = f'{date_log}_wedo_badminton_balance.csv'
        FOLDER_DATE = os.path.join(FOLDER_PROJECT, 'account', 'by_date')
        if not os.path.exists(FOLDER_DATE):
            os.makedirs(FOLDER_DATE)
        PATH_ACCOUNT_DATE = os.path.join(FOLDER_DATE, filename_balance)
        dfBalancePlayerWrite.to_csv(PATH_ACCOUNT_DATE, index=False)
        # write to onedrive
        # PATH_ACCOUNT_DATE_ONEDRIVE = os.path.join(FOLDER_BADMINTON_ONEDRIVE, 'account', 'by_date', filename_balance)
        # dfBalancePlayerWrite.to_csv(PATH_ACCOUNT_DATE_ONEDRIVE, index=False)

        # move listplayer to checked
        if MODE == 'update':
            path_listplayer_new = os.path.join(FOLDER_PROJECT, folder_file, 'checked', filename_listplayer)
            os.rename(path_file_listplayer, path_listplayer_new)

        # write balance current
        filename = 'wedo_badminton_balance.csv'
        path_write = os.path.join(FOLDER_PROJECT, 'account', filename)
        dfBalancePlayerWrite.to_csv(path_write, index=False)

        print("Generating image....")
        path_script = os.path.join(FOLDER_PROJECT, 'tools', 'export_image_current.py')
        os.system(f"python {path_script}")

else:
    print("file is checklist player is empty !")

print("#----- Finished Main-----#")