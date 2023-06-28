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

UPDATE_FROM_CURRENT = True
FORCE_WRITE_PLAYER_HISTORY = False
MOVE_CHECKED = True
FOLDER_BADMINTON_ONEDRIVE = os.path.join(r'C:\Users\Panna\OneDrive\Projects\badminton-payment')

# load balance
if UPDATE_FROM_CURRENT:
    path_read = os.path.join(FOLDER_PROJECT, 'account', 'wedo_badminton_balance.csv')

else:  
    path_read = os.path.join(FOLDER_PROJECT, 'account', 'initial', 'account_balance_init.csv')
 
dfBalance = pd.read_csv(path_read)
list_playercode_balance = list(dfBalance['player_code'].unique())
dfBalancePlayer = dfBalance.copy()
dfBalancePlayer['player_index'] = dfBalancePlayer['player_code']
dfBalancePlayer.set_index('player_index', inplace=True)

# load daily player checklist
folder_player_checker = os.path.join(FOLDER_PROJECT, 'player')
list_dir, list_folder, list_file = wedolib.findFile(folder_player_checker, '*.xlsx')

if len(list_file) > 0:
    # sort by date
    for ifile in range(len(list_file)):
        filename_listplayer = list_file[ifile]
        date_log = filename_listplayer.split('_')[0]

        folder_file = list_folder[ifile]
        path_file_listplayer = list_dir[ifile]
        dfPlayerCome = pd.read_excel(path_file_listplayer)
        list_playercode_come = list(dfPlayerCome['player_code'].unique())
        # dfPlayerCome2 = dfPlayerCome.set_index('player_code')

        n_player = dfPlayerCome.shape[0]
        
        price_per_player = dfPlayerCome.iloc[0]['price_per_player']

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

            print(f'{date_log} {player_code}')

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
            PATH_ACCOUNT_PLAYER = os.path.join(FOLDER_PROJECT, 'account', 'by_player', filename_player_balance)
            PATH_ACCOUNT_PLAYER_ONEDRIVE = os.path.join(FOLDER_BADMINTON_ONEDRIVE, 'account', 'by_player', filename_player_balance)
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
                dfBalancePlayerHist = dfBalancePlayerHist.append(dfBalancePlayerHistNew)
                dfBalancePlayerHist.to_csv(PATH_ACCOUNT_PLAYER, index=False)
                dfBalancePlayerHist.to_csv(PATH_ACCOUNT_PLAYER_ONEDRIVE, index=False)

            else:
                # create new 
                dfBalancePlayerHistNew.to_csv(PATH_ACCOUNT_PLAYER, index=False)
                dfBalancePlayerHistNew.to_csv(PATH_ACCOUNT_PLAYER_ONEDRIVE, index=False)
                # dfBalancePlayerHist.to_csv(PATH_ACCOUNT_PLAYER, )
                # dfBalancePlayerHist.columns = dfBalancePlayerHist.iloc[0]

        # add new player
        dfNewPlayer = pd.DataFrame(dictNewPlayer)
        dfBalancePlayerWrite = dfBalancePlayer.append(dfNewPlayer, ignore_index=True)

        # write balance date
        filename_balance = f'{date_log}_wedo_badminton_balance.csv'
        PATH_ACCOUNT_DATE = os.path.join(FOLDER_PROJECT, 'account', 'by_date', filename_balance)
        dfBalancePlayerWrite.to_csv(PATH_ACCOUNT_DATE, index=False)
        # write to onedrive
        PATH_ACCOUNT_DATE_ONEDRIVE = os.path.join(FOLDER_BADMINTON_ONEDRIVE, 'account', 'by_date', filename_balance)
        dfBalancePlayerWrite.to_csv(PATH_ACCOUNT_DATE_ONEDRIVE, index=False)

        # move listplayer to checked
        path_listplayer_new = os.path.join(FOLDER_PROJECT, folder_file, 'checked', filename_listplayer)
        if MOVE_CHECKED:
            os.rename(path_file_listplayer, path_listplayer_new)

    # write balance current
    filename = 'wedo_badminton_balance.csv'
    path_write = os.path.join(FOLDER_PROJECT, 'account', filename)
    dfBalancePlayerWrite.to_csv(path_write, index=False)

else:
    print("file is checklist player is empty !")

# filename = 'wedo_badminton_balance_sorted.csv'
# path_write = os.path.join(FOLDER_PROJECT, 'account', filename)
# dfBalancePlayerWrite.sort('balance', reversed=True)
# dfBalancePlayerWrite.to_csv(path_write)

print("Generating image....")
path_script = os.path.join(FOLDER_PROJECT, 'tools', 'export_image_current.py')
os.system(f"python {path_script}")

print("#----- Finished Main-----#")