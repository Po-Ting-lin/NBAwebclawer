# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 10:37:17 2019
purpose: EFF, PER
@author: BT
"""
import sys
from nba_players_class import SCRAPPING, ANALYSIS, PLAYER_MEAN_TABLE, POOL


ana = SCRAPPING()
conn,session = ana.call_session()

###############################################################################
# best data
# session = ana.ana_best()

year, month, day = [2019, 3, 23]

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


session_ana.commit()
conn_ana.dispose()

###############################################################################

#
# #calculate the data mean for each players in league
# accu_list = ['ontime','PTS','AST','STL','BLK','FGA','FGM','FTA','FTM','TPA','TPM','ORB','DRB','TOV','PF','plusminus','aPER','EFF']
# data_accumulated = dict()
# for accu_data in accu_list:
#     data_accumulated.update({accu_data:[0]*10})
# for player in session.query(NBASTORAGE).all():
#     for i in range(10):
#         partition = 0
#         if total_MP_allplayer[i] != 0:
#             exec("partition = (player.ontime"+str(i)+"/total_MP_allplayer["+str(i)+"])")
#             for col in accu_list:
#                 exec("data_accumulated['"+col+"']["+str(i)+"] += partition*player."+col+str(i))
#
#
# #average data_accumulated
# data_mean = dict()
# for accu_data in accu_list:
#     buffer = []
#     for i in range(10):
#         if data_accumulated[accu_data][i] != 0:
#             buffer.append(data_accumulated[accu_data][i])
#     data_mean.update({accu_data:float(np.mean(buffer))})
#
# #update session
# if not session.query(PLAYER_MEAN_TABLE).filter(PLAYER_MEAN_TABLE.name == 'mean').first():
#     tem = PLAYER_MEAN_TABLE('mean',data_mean['ontime'],data_mean['PTS'],data_mean['AST'],data_mean['STL'],data_mean['BLK'],data_mean['FGA'],data_mean['FGM'],data_mean['FTA'],data_mean['FTM'],data_mean['TPA'],data_mean['TPM'],data_mean['ORB'],data_mean['DRB'],data_mean['TOV'],data_mean['PF'],data_mean['plusminus'],data_mean['aPER'],15.0,data_mean['EFF'])
#     session.add(tem)
# else:
#     for col in accu_list:
#         exec("session.query(PLAYER_MEAN_TABLE).filter(PLAYER_MEAN_TABLE.name == 'mean').update({PLAYER_MEAN_TABLE."+col+": data_mean['"+col+"']})")
#
# # why??
# #accumulate PER
# for accu_data in ['PER']:
#     data_accumulated.update({accu_data:[0]*10})
# for player in session.query(NBASTORAGE).all():
#     for i in range(10):
#         partition = 0
#         if total_MP_allplayer[i] != 0:
#             exec("partition = (player.ontime"+str(i)+"/total_MP_allplayer["+str(i)+"])")
#             for col in ['PER']:
#                 exec("data_accumulated['"+col+"']["+str(i)+"] += partition*player."+col+str(i))
# #average and update session PER
# for accu_data in ['PER']:
#     buffer = []
#     for i in range(10):
#         if data_accumulated[accu_data][i] != 0:
#             buffer.append(data_accumulated[accu_data][i])
#     data_mean.update({accu_data:float(np.mean(buffer))})
# session.query(PLAYER_MEAN_TABLE).update({PLAYER_MEAN_TABLE.PER: data_mean['PER']})

###############################################################################

# session.commit()
# conn.dispose()

###############################################################################
# #after analysis, percentage of each player in league
# ana = SCRAPPING()
# conn, session = ana.call_session()
# print("Calculate the percentage of each player in league")
# session = ana.mean_of_each_player_analysis()
# session.commit()
# conn.dispose()
