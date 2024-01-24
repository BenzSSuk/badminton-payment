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
FOLDER_PROJECT = checkSysPathAndAppend(folderFile, 1)

FOLDER_SRC = pjoin(FOLDER_PROJECT, 'src')

SYNC_CLOUD = True

if SYNC_CLOUD:
    # ---------- Payment ---------- #
    # sync player payment from google from (response in google sheet)
    subfolder = 'payment'
    filename = 'sync_payment_ggform.py'
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()

    # update balance with payment from google form
    subfolder = 'payment'
    filename = 'update_balance_from_payment.py'
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()

    # ---------- Check Player ---------- #
    # sync player&shuttlecock record from google sheet
    subfolder = 'record'
    filename = 'sync_record_ggsheet.py'
    PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
    sp_obj = subprocess.run(['python', PATH_SCRIPT])
    sp_obj.check_returncode()

# ---------- Billing ---------- #
# generate original listplayer.xlsx
subfolder = 'billing'
filename = 'gen_listplayer_from_ggsheet.py'
PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
sp_obj = subprocess.run(['python', PATH_SCRIPT])
sp_obj.check_returncode()

# update balance after billing 
subfolder = 'billing'
filename = 'update_balance.py'
PATH_SCRIPT = pjoin(FOLDER_SRC, subfolder, filename)
sp_obj = subprocess.run(['python', PATH_SCRIPT])
sp_obj.check_returncode()
print("#----- Finish Main -----#")