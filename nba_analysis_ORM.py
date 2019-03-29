# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 10:37:17 2019
purpose: EFF, PER
@author: BT
"""
from nba_players_class import SCRAPPING, ANALYSIS, PLAYER_PERCENTAGE_TABLE, POOL


###############################################################################
# best data
# session = ana.ana_best()

year, month, day = [2019, 3, 29]

ana_obj = ANALYSIS(year, month, day)
conn_ana, session_ana = ana_obj.call_session()

# best data
session_ana = ana_obj.ana_best()

# eff
session_ana = ana_obj.eff_calculation()

# PER calculation
session_ana = ana_obj.league_parameter_calculation()
session_ana = ana_obj.team_parameter_calculation()
session_ana = ana_obj.a_per_calculation()
session_ana = ana_obj.per_calculation()


# find name
namelist = ana_obj.find_name()

# compress 1 game
test_space, session_ana = ana_obj.compresstime_of_each_player(1, namelist)
session_ana.commit()
conn_ana.dispose()

# compress all time to be a baseline
ana_obj = ANALYSIS(year, month, day)
conn_ana, session_ana = ana_obj.call_session()
test_space, session_ana = ana_obj.compresstime_of_each_player(-1, namelist)
session_ana.commit()
conn_ana.dispose()

# beacause data could confuse without commit!
ana_obj = ANALYSIS(year, month, day)
conn_ana, session_ana = ana_obj.call_session()
session_ana = ana_obj.compress_all_player_all_time()
session_ana.commit()
conn_ana.dispose()

###############################################################################
