import os
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go

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
FOLDER_PROJECT = checkSysPathAndAppend(folderFile, 1)

# FOLDER_IMG_RECORD = os.path.join(r'C:\Users\Panna\OneDrive\Projects\badminton-payment\image_record')
FOLDER_IMG_RECORD_LOCAL = os.path.join(FOLDER_PROJECT, 'image_record')

import lib.DataProcessing as wedolib

# load daily player checklist
folder_player_checked = os.path.join(FOLDER_PROJECT, 'account', 'by_date')
list_dir, list_folder, list_file = wedolib.findFile(folder_player_checked, '*.csv', 0)
list_dir.sort()
list_folder.sort()
list_file.sort()
filename_balance_lasted = list_file[-1]
lasted_date = filename_balance_lasted.split("_")[0]

filename_player_lasted = f'{lasted_date}_listplayer.xlsx'
path_file = os.path.join(FOLDER_PROJECT, 'player', 'checked', filename_player_lasted)
dfPlayerCurrent = pd.read_excel(path_file)

# ---------- Shuttle ----------
print('Generating image shuttlecock used...')
dfShuttle = dfPlayerCurrent.iloc[0].iloc[6:12]

#Creating the figure. Setting a small pad on the tight layout
dict_header = {
    'values': ['', 'amount'],
    'height': 30,
    'fill_color': 'green',
    'align': 'left',
    'font': {
        'color': 'black',
        'size': 15
    }
}
dict_cell = {
    'values': [dfShuttle.index.to_list(), 
               dfShuttle.to_list()],
    'height': 30,
    'fill_color': 'lavender',
    'align': 'left',
    'font': {
        'color': 'black',
        'size': 15
    }
}
fig = go.Figure(data=[go.Table(
                        columnorder = [1, 2],
                        columnwidth = [40, 40],
                        header=dict_header,
                        cells=dict_cell)],
                layout=go.Layout(title=dict(text=f'{lasted_date}_จำนวนลูกใช้',
                                            font=dict(family="Arial",
                                                    size=30,
                                                    color='#000000'
                                                    )
                                            ),
                                            width=450,
                                            height=400
                                )
                )

# FOLDER_IMG_RECORD_DATE = os.path.join(FOLDER_IMG_RECORD, lasted_date)
# if not os.path.exists(FOLDER_IMG_RECORD_DATE):
#     os.makedirs(FOLDER_IMG_RECORD_DATE)
FOLDER_IMG_RECORD_DATE_LOCAL = os.path.join(FOLDER_IMG_RECORD_LOCAL, lasted_date)
if not os.path.exists(FOLDER_IMG_RECORD_DATE_LOCAL):
    os.makedirs(FOLDER_IMG_RECORD_DATE_LOCAL)

filename = f'{lasted_date}_shuttlecock_used.png'

PATH_IMG_SHUTTLE = os.path.join(FOLDER_IMG_RECORD_DATE_LOCAL, filename)
fig.write_image(PATH_IMG_SHUTTLE)

# PATH_IMG_SHUTTLE = os.path.join(FOLDER_IMG_RECORD_DATE, filename)
# fig.write_image(PATH_IMG_SHUTTLE)

# ---------- Player balance ----------
print('Generating image player balance...')
path_file = os.path.join(FOLDER_PROJECT, 'account', 'by_date', f'{lasted_date}_wedo_badminton_balance.csv')
dfBalance = pd.read_csv(path_file)

dfBalance.sort_values(by=['team', 'player_name'], inplace=True, ignore_index=True)
dfBalance.index = dfBalance.index + 1
# dfBalance.reset_index(inplace=True)

n_player_per_page = 20
n_row = dfBalance.shape[0]
n_plot = int(np.ceil(n_row/n_player_per_page))
count_page = 0
for i in range(n_plot):
    '''
    1 0  -  19
    2 20 -  39
    
    '''
    count_page = count_page + 1
    istr = i*n_player_per_page
    iend = istr + n_player_per_page
    if iend > n_row:
        iend = n_row
    dfBalancePage = dfBalance.iloc[istr:iend]
    dict_header = {
        'values': ['index', 'team', 'name', 'balance'],
        'height': 30,
        'fill_color': 'paleturquoise',
        'align': 'left',
        'font': {
            'color': 'black',
            'size': 15
        }
    }
    dict_cell = {
        'values': [dfBalancePage.index,
                    dfBalancePage['team'].to_list(), 
                    dfBalancePage['player_name'].to_list(),
                    dfBalancePage['balance'].to_list()],
        'height': 30,
        'fill_color': 'lavender',
        'align': 'left',
        'font': {
            'color': 'black',
            'size': 15
        }
    }
    fig = go.Figure(data=[go.Table(
                            columnwidth = [40, 40, 40],
                            header=dict_header,
                            cells=dict_cell)],
                    layout=go.Layout(title=dict(text=f'{lasted_date}_player_balance_{count_page}',
                                                font=dict(family="Arial",
                                                        size=30,
                                                        color='#000000'
                                                        )
                                                ),
                                                width=500,
                                                height=800
                                    )
                    )
    filename = f'{lasted_date}_player_balance_{count_page}.png'

    PATH_IMG_BALANCE = os.path.join(FOLDER_IMG_RECORD_DATE_LOCAL, filename)
    fig.write_image(PATH_IMG_BALANCE)

    # PATH_IMG_BALANCE = os.path.join(FOLDER_IMG_RECORD_DATE, filename)
    # fig.write_image(PATH_IMG_BALANCE)

print("# ----- Finished ----- #")