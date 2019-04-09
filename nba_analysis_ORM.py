# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 10:37:17 2018
Purpose: compute EFF, PER, average, and the best data
@author: BT
"""
from nba_players_class import ANALYSIS, PLAYER_PERCENTAGE_TABLE, POOL
import time

###############################################################################
# best data
# session = ana.ana_best()

# get the local time
year, month, day = list(map(int, time.strftime("%Y %m %d", time.localtime()).split(" ")))
print(year, month, day, 'analysis...')


# init
ana_obj = ANALYSIS(year, month, day)
conn_ana, session_ana = ana_obj.call_session()

# best data
session_ana = ana_obj.ana_best()

# eff
session_ana = ana_obj.eff_calculation()

# find name of all players
namelist = ana_obj.find_name()

# PER calculation
session_ana = ana_obj.league_parameter_calculation()
session_ana = ana_obj.team_parameter_calculation()
session_ana = ana_obj.a_per_calculation()
session_ana.commit()
lg_aper = ana_obj.lg_aPER_compute(namelist)
session_ana = ana_obj.per_calculation(lg_aper)
session_ana.commit()

# compress 1 game
test_space, session_ana = ana_obj.compresstime_of_each_player(1, namelist)
session_ana.commit()

# compress all time to be a baseline
test_space, session_ana = ana_obj.compresstime_of_each_player(-1, namelist)
session_ana.commit()

# because data could confuse without commit!
session_ana = ana_obj.compress_all_player_all_time()
session_ana.commit()

# connection disable
conn_ana.dispose()

###############################################################################
