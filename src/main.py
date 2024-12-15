import os
from os.path import join as pjoin
import sys
import pandas as pd
import subprocess
import time

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
FOLDER_PROJECT = checkSysPathAndAppend(folderFile, 1)

FOLDER_SRC = pjoin(FOLDER_PROJECT, 'src')

'''
auto          : - sync player payment&log on cloud to local
                - process file from cloud to original excel
                - update balance from excel
local         : - process file from cloud to original excel
                - update balance from excel
'''

MODE = 'auto' 
if len(sys.argv) > 1:
    MODE = sys.argv[1]

list_dict_script = [
    {
        "task_info": "sync log file from ggsheet",
        "folder": pjoin("src", "ggsheet"),
        "script_name": "sync_ggsheet.py",
        "mode": ["auto", "sync"]
    },
    {
        "task_info": "split raw_log.csv file to log_day.csv",
        "folder": pjoin("src", "ggsheet"),
        "script_name": "split_log_day.py",
        "mode": ["auto", "local"]
    },
    {
        "task_info": "convert log_day.csv to log_day.excel",
        "folder": pjoin("src", "ggsheet"),
        "script_name": "gen_billing_per_day.py",
        "mode": ["auto", "local"]
    },
    {
        "task_info": "update account from player payment",
        "folder": pjoin("src", "account"),
        "script_name": "update_account_from_payment.py",
        "mode": ["auto", "local"]
    },
    {
        "task_info": "update account from player billing",
        "folder": pjoin("src", "account"),
        "script_name": "update_account_from_billing.py",
        "mode": ["auto", "local"]
    },
    {
        "task_info": "generate player's lasted account balance",
        "folder": pjoin("src", "account"),
        "script_name": "gen_lasted_account_balance.py",
        "mode": ["auto", "local"]
    },
    {
        "task_info": "generate image balance",
        "folder": pjoin("src", "billing"),
        "script_name": "gen_img_balance.py",
        "mode": ["auto", "local"]
    }   
]

def run_python(path_script, time_delay=0.5):
    sp_obj = subprocess.run(['python', path_script])
    sp_obj.check_returncode()
    time.sleep(time_delay)

for dict_script in list_dict_script:
    print(dict_script['task_info'])
    print(pjoin(dict_script['folder'], dict_script['script_name']))

    if MODE in dict_script['mode']:
        path_script = pjoin(FOLDER_PROJECT, dict_script['folder'], dict_script['script_name'])
        run_python(path_script)
