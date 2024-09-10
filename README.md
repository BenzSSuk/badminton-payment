# badminton-payment
Script for logging payment  history

# 1. Sync Payment from ggsheet
- src/payment/sync_payment_ggform.py'
- Sync ggsheet to file record/payment/ggform

# 2. Update balanece from payment
- src/payment/update_balance_from_payment.py
- update account/wedo_badminton_balance.csv and account/by_player

# 3. Sync player record from ggsheet
- src/record/sync_record_ggsheet.py
- save file to data/cloud/player (not seperated day)
- save file seperate xxx_log_day.csv to record/player/ggsheet (seperate day)

# 4. generate excel listplayer
- src/billing/gen_listplayer_from_ggsheet.py
- convert xxx_log_day.csv to log_player.xlsx

# 5 
- src/billing/update_balance.py
- 