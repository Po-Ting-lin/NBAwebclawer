# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 10:37:17 2019
purpose: EFF, PER
@author: BT
"""
import sys
from nba_players_class import SCRAPPING, ANALYSIS


ana = SCRAPPING()
conn,session = ana.call_session()

###############################################################################
# best data
# session = ana.ana_best()

ana_obj = ANALYSIS()

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
# ######uPER


# ##league constant factor
# #query object
# bb = session.query(LEAGUE_TABLE)
# #LEAGUE_TABLE object
# b = bb.first()
# #to show the feasibility of offense among past and future
# factor = (2/3)-(0.5*(b.ast_per_g/b.fgm_per_g))/(2*(b.fgm_per_g/b.ftm_per_g))
# #value of possession, to show the eff of offense among all player(league)
# VOP = b.pts_per_g / (b.fga_per_g - b.orb_per_g + b.tov_per_g + 0.44*b.fta_per_g)
# #defensive rebound percentage, to show the ability of defense among all player
# DRBP = ((b.drb_per_g+b.orb_per_g)-b.orb_per_g)/(b.drb_per_g+b.orb_per_g)
# #update to session
# bb.update({LEAGUE_TABLE.factor: factor, LEAGUE_TABLE.VOP: VOP, LEAGUE_TABLE.DRBP: DRBP})
###############################################################################
# ##team constant factor
# totalteam_list = ['ATL','BRK','BOS','CHO','CHI','CLE','DAL','DEN','DET','GSW','HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL','PHI','PHO','POR','SAC','SAS','TOR','UTA','WAS']
# cc = session.query(TEAM_TABLE)
# for t in totalteam_list:
#     #query. eg: ATL and oppATL
#     cc_query = cc.filter(or_(TEAM_TABLE.teamsname == t,TEAM_TABLE.teamsname == 'opp'+t))
#     #select one
#     t_obj = cc_query.all()[0]
#     o_obj = cc_query.all()[1]
#     #Possessions(Poss)
#     tmPoss = t_obj.fga_per_g + 0.4*t_obj.fta_per_g - 1.07*(t_obj.orb_per_g/(t_obj.orb_per_g+o_obj.drb_per_g))*(t_obj.fga_per_g-t_obj.fgm_per_g) + t_obj.tov_per_g
#     oppPoss = o_obj.fga_per_g + 0.4*o_obj.fta_per_g - 1.07*(o_obj.orb_per_g/(o_obj.orb_per_g+t_obj.drb_per_g))*(o_obj.fga_per_g-o_obj.fgm_per_g) + o_obj.tov_per_g
#     #pace factor
#     tmPace = 48*((tmPoss+oppPoss)/(2*(t_obj.mp_per_g/5)))
#     #update to session
#     cc_query.filter(TEAM_TABLE.teamsname == t).update({TEAM_TABLE.tmPOSS:tmPoss, TEAM_TABLE.oppPOSS:oppPoss, TEAM_TABLE.tmPACE:tmPace})
#     print(t,' tmPACE is ',cc_query.filter(TEAM_TABLE.teamsname == t).first().tmPACE)
###############################################################################
##main
#LEAGUE object--> b.
#team query--> cc.
# for player in session.query(NBASTORAGE).all():
#     #team object eg: t_obj.ast_per_g
#     #player object eg: player.AST
#     t_obj = cc.filter(TEAM_TABLE.teamsname == player.team).first()
#     if not t_obj:
#         sys.exit(player.playersname+'cannot find his team!')
#     for i in range(10): #each game
#
#         #unadjusted PER
#         exec("time_tem = player.ontime"+str(i))
#         if player.ontime0 >= 5:
#             r_min = (1/player.ontime0)
#         else:
#             r_min = 0
#
#         exec("block1 = player.TPM"+str(i))
#         exec("block2 = (2/3)*player.AST"+str(i))
#         #(tmAST/tmFGM) is that the preference of scoring from otehrs AST or personal offense
#         preference_of_scoring = (t_obj.ast_per_g/t_obj.fgm_per_g)
#         exec("block3 = (2 - factor*preference_of_scoring)*player.FGM"+str(i))
#         #free throw considering (tmAST/tmFG)
#         exec("block4 = (player.FTM"+str(i)+"*0.5*(2-(1/3)*preference_of_scoring))")
#         #turnovers
#         exec("block5 = VOP*player.TOV"+str(i))
#         #missing field goal
#         exec("block6 = VOP*DRBP*(player.FGA"+str(i)+"-player.FGM"+str(i)+")")
#         #missing free throw
#         exec("block7 = VOP*0.44*(0.44+(0.56*DRBP))*(player.FTA"+str(i)+"-player.FTM"+str(i)+")")
#         #defense rebounds
#         exec("total_RB = player.ORB"+str(i)+" + player.DRB"+str(i))
#         exec("block8 = VOP*(1-DRBP)*(total_RB - player.ORB"+str(i)+")")
#         #offense rebounds
#         exec("block9 = VOP*DRBP*player.ORB"+str(i))
#         #steal
#         exec("block10 = VOP*player.STL"+str(i))
#         #block considering defense rebounds
#         exec("block11 = VOP*DRBP*player.BLK"+str(i))
#         #fouls considering the effect after foul
#         exec("block12 = player.PF"+str(i)+"*((b.ftm_per_g/b.pf_per_g)-0.44*(b.fta_per_g/b.pf_per_g)*VOP)")
#         uPER = r_min*(block1+block2+block3+block4-block5-block6-block7+block8+block9+block10+block11-block12)
#         #aPER
#         aPER = round(uPER*(b.pace/t_obj.tmPACE),2)
#         exec("aa.filter(NBASTORAGE.playersname == player.playersname).update({NBASTORAGE.aPER"+str(i)+": aPER})")
#         print('calculate',player.playersname,"'s aPER"+str(i)+": ",aPER)
###############################################################################
# ##calculate lg_aPER(sigma(MPi*aPERi/Min))
# #refresh it
# aa = session.query(NBASTORAGE)
# a = aa.all()
# #total_MP_allplayer
# total_MP_allplayer = [0]*10
# for player in a:
#     for game in range(10):
#         exec("total_MP_allplayer["+str(game)+"] += player.ontime"+str(game))
# print('total_MP_allplayer0:',total_MP_allplayer[0],'total_MP_allplayer1:',total_MP_allplayer[1])
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
# # ###calculate PER
# # for player in a:
# #     for i in range(10):
# #         if data_accumulated['aPER'][i] != 0:
# #             exec("PER = round(player.aPER0*(15/data_accumulated['aPER']["+str(i)+"]),2)")
# #         elif data_accumulated['aPER'][i] == 0:
# #             PER = 0
# #         exec("aa.filter(NBASTORAGE.playersname == player.playersname).update({NBASTORAGE.PER"+str(i)+": PER})")
# #     print(player.playersname,"'s PER is: ",player.PER0)
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

session.commit()
conn.dispose()

###############################################################################
#after analysis, percentage of each player in league
ana = SCRAPPING()
conn, session = ana.call_session()
print("Calculate the percentage of each player in league")
session = ana.mean_of_each_player_analysis()
session.commit()
conn.dispose()
