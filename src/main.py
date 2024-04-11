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
auto_local    : - process file from cloud to original excel
                - update balance from excel
manual_excel  : - update balance from excel
'''

MODE = 'auto' 
if len(sys.argv) > 1:
    MODE = sys.argv[1]

t_offset_script = 3

mode_config_all = {
    "auto": {
        "sync_cloud": True,
        "process_file_cloud": True,
        "update_balance": True
    },
    "auto_local": {
        "sync_cloud": False,
        "process_file_cloud": True,
        "update_balance": True
    },
    "manual_excel": {
        "sync_cloud": False,
        "process_file_cloud": False,
        "update_balance": True
    }
}
mode_config = mode_config_all[MODE]

if mode_config['sync_cloud']:
    # ---------- Payment ---------- #
    # sync player payment from google from (response in google sheet)
    subfolder = 'payment'
    filename = 'sync_payment_ggform.py'
    print(filename)
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()
    time.sleep(t_offset_script)

if mode_config['process_file_cloud']:
    # update balance with payment from google form
    subfolder = 'payment'
    filename = 'update_balance_from_payment.py'
    print(filename)
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()
    time.sleep(t_offset_script)

if mode_config['sync_cloud']:
    # ---------- Check Player ---------- #
    # sync player&shuttlecock record from google sheet
    subfolder = 'record'
    filename = 'sync_record_ggsheet.py'
    print(filename)
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()
    time.sleep(t_offset_script)

# ---------- Billing ---------- #
# generate original listplayer.xlsx
if mode_config['process_file_cloud']:
    subfolder = 'billing'
    filename = 'gen_listplayer_from_ggsheet.py'
    print(filename)
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()
    time.sleep(t_offset_script)

if mode_config['update_balance']:
    # update balance after billing 
    subfolder = 'billing'
    filename = 'update_balance.py'
    print(filename)
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()
    print("#----- Finish Main -----#")
    time.sleep(t_offset_script)