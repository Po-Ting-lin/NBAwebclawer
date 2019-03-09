# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 18:55:08 2019
purpose: visualize the data
@author: BT
"""
from dbdb.nba_players_class import SCRAPPING,TEAM_TABLE,LEAGUE_TABLE,NBASTORAGE,PLAYER_MEAN_TABLE

def comparewithmean(input_player):
    scrape = SCRAPPING()
    conn, session = scrape.call_session()
    aa = session.query(NBASTORAGE)
    playermean = session.query(PLAYER_MEAN_TABLE).first()

    #input player to be a list
    player_list = []
    for player in aa.all():
        if input_player in player.playersname:
            player_list.append(player)

    print('player_list including: ')
    for i in player_list:
        print(i.playersname)

    plot_mom_list = []
    for player in player_list:
        this_player_totaltime = 0
        this_player_totaltime += player.ontime0
        this_player_totaltime += player.ontime1
        this_player_totaltime += player.ontime2
        this_player_totaltime += player.ontime3
        this_player_totaltime += player.ontime4
        this_player_totaltime += player.ontime5
        this_player_totaltime += player.ontime6
        this_player_totaltime += player.ontime7
        this_player_totaltime += player.ontime8
        this_player_totaltime += player.ontime9

        # print('ometime:',player.ontime0,player.ontime1,player.ontime2)
        # print('this_player_totaltime:', this_player_totaltime)

        #ontime of each player in each game ratio
        partition = [0]*10
        aaaa = ['ontime','PTS','AST','STL','BLK','FGA','FGM','FTA','FTM','TPA','TPM','ORB','DRB','TOV','PF','plusminus','aPER','PER','EFF']
        
        partition[0] = (player.ontime0 / this_player_totaltime)
        partition[1] = (player.ontime1 / this_player_totaltime)
        partition[2] = (player.ontime2 / this_player_totaltime)
        partition[3] = (player.ontime3 / this_player_totaltime)
        partition[4] = (player.ontime4 / this_player_totaltime)
        partition[5] = (player.ontime5 / this_player_totaltime)
        partition[6] = (player.ontime6 / this_player_totaltime)
        partition[7] = (player.ontime7 / this_player_totaltime)
        partition[8] = (player.ontime8 / this_player_totaltime)
        partition[9] = (player.ontime9 / this_player_totaltime)
        mean_data = dict()
        
        #ontime
        buffer = 0.0
        buffer += partition[0] * player.ontime0
        buffer += partition[1] * player.ontime1
        buffer += partition[2] * player.ontime2
        buffer += partition[3] * player.ontime3
        buffer += partition[4] * player.ontime4
        buffer += partition[5] * player.ontime5
        buffer += partition[6] * player.ontime6
        buffer += partition[7] * player.ontime7
        buffer += partition[8] * player.ontime8
        buffer += partition[9] * player.ontime9
        mean_data.update({'ontime': buffer})
        #PTS
        buffer = 0.0
        buffer += partition[0] * player.PTS0
        buffer += partition[1] * player.PTS1
        buffer += partition[2] * player.PTS2
        buffer += partition[3] * player.PTS3
        buffer += partition[4] * player.PTS4
        buffer += partition[5] * player.PTS5
        buffer += partition[6] * player.PTS6
        buffer += partition[7] * player.PTS7
        buffer += partition[8] * player.PTS8
        buffer += partition[9] * player.PTS9
        mean_data.update({'PTS': buffer})
        #AST
        buffer = 0.0
        buffer += partition[0] * player.AST0
        buffer += partition[1] * player.AST1
        buffer += partition[2] * player.AST2
        buffer += partition[3] * player.AST3
        buffer += partition[4] * player.AST4
        buffer += partition[5] * player.AST5
        buffer += partition[6] * player.AST6
        buffer += partition[7] * player.AST7
        buffer += partition[8] * player.AST8
        buffer += partition[9] * player.AST9
        mean_data.update({'AST': buffer})
        #STL
        buffer = 0.0
        buffer += partition[0] * player.STL0
        buffer += partition[1] * player.STL1
        buffer += partition[2] * player.STL2
        buffer += partition[3] * player.STL3
        buffer += partition[4] * player.STL4
        buffer += partition[5] * player.STL5
        buffer += partition[6] * player.STL6
        buffer += partition[7] * player.STL7
        buffer += partition[8] * player.STL8
        buffer += partition[9] * player.STL9
        mean_data.update({'STL': buffer})
        #BLK
        buffer = 0.0
        buffer += partition[0] * player.BLK0
        buffer += partition[1] * player.BLK1
        buffer += partition[2] * player.BLK2
        buffer += partition[3] * player.BLK3
        buffer += partition[4] * player.BLK4
        buffer += partition[5] * player.BLK5
        buffer += partition[6] * player.BLK6
        buffer += partition[7] * player.BLK7
        buffer += partition[8] * player.BLK8
        buffer += partition[9] * player.BLK9
        mean_data.update({'BLK': buffer})
        #FGA
        buffer = 0.0
        buffer += partition[0] * player.FGA0
        buffer += partition[1] * player.FGA1
        buffer += partition[2] * player.FGA2
        buffer += partition[3] * player.FGA3
        buffer += partition[4] * player.FGA4
        buffer += partition[5] * player.FGA5
        buffer += partition[6] * player.FGA6
        buffer += partition[7] * player.FGA7
        buffer += partition[8] * player.FGA8
        buffer += partition[9] * player.FGA9
        mean_data.update({'FGA': buffer})
        #FGM
        buffer = 0.0
        buffer += partition[0] * player.FGM0
        buffer += partition[1] * player.FGM1
        buffer += partition[2] * player.FGM2
        buffer += partition[3] * player.FGM3
        buffer += partition[4] * player.FGM4
        buffer += partition[5] * player.FGM5
        buffer += partition[6] * player.FGM6
        buffer += partition[7] * player.FGM7
        buffer += partition[8] * player.FGM8
        buffer += partition[9] * player.FGM9
        mean_data.update({'FGM': buffer})
        #FTA
        buffer = 0.0
        buffer += partition[0] * player.FTA0
        buffer += partition[1] * player.FTA1
        buffer += partition[2] * player.FTA2
        buffer += partition[3] * player.FTA3
        buffer += partition[4] * player.FTA4
        buffer += partition[5] * player.FTA5
        buffer += partition[6] * player.FTA6
        buffer += partition[7] * player.FTA7
        buffer += partition[8] * player.FTA8
        buffer += partition[9] * player.FTA9
        mean_data.update({'FTA': buffer})
        #FTM
        buffer = 0.0
        buffer += partition[0] * player.FTM0
        buffer += partition[1] * player.FTM1
        buffer += partition[2] * player.FTM2
        buffer += partition[3] * player.FTM3
        buffer += partition[4] * player.FTM4
        buffer += partition[5] * player.FTM5
        buffer += partition[6] * player.FTM6
        buffer += partition[7] * player.FTM7
        buffer += partition[8] * player.FTM8
        buffer += partition[9] * player.FTM9
        mean_data.update({'FTM': buffer})
        #TPA
        buffer = 0.0
        buffer += partition[0] * player.TPA0
        buffer += partition[1] * player.TPA1
        buffer += partition[2] * player.TPA2
        buffer += partition[3] * player.TPA3
        buffer += partition[4] * player.TPA4
        buffer += partition[5] * player.TPA5
        buffer += partition[6] * player.TPA6
        buffer += partition[7] * player.TPA7
        buffer += partition[8] * player.TPA8
        buffer += partition[9] * player.TPA9
        mean_data.update({'TPA': buffer})
        #TPM
        buffer = 0.0
        buffer += partition[0] * player.TPM0
        buffer += partition[1] * player.TPM1
        buffer += partition[2] * player.TPM2
        buffer += partition[3] * player.TPM3
        buffer += partition[4] * player.TPM4
        buffer += partition[5] * player.TPM5
        buffer += partition[6] * player.TPM6
        buffer += partition[7] * player.TPM7
        buffer += partition[8] * player.TPM8
        buffer += partition[9] * player.TPM9
        mean_data.update({'TPM': buffer})
        #ORB
        buffer = 0.0
        buffer += partition[0] * player.ORB0
        buffer += partition[1] * player.ORB1
        buffer += partition[2] * player.ORB2
        buffer += partition[3] * player.ORB3
        buffer += partition[4] * player.ORB4
        buffer += partition[5] * player.ORB5
        buffer += partition[6] * player.ORB6
        buffer += partition[7] * player.ORB7
        buffer += partition[8] * player.ORB8
        buffer += partition[9] * player.ORB9
        mean_data.update({'ORB': buffer})
        #DRB
        buffer = 0.0
        buffer += partition[0] * player.DRB0
        buffer += partition[1] * player.DRB1
        buffer += partition[2] * player.DRB2
        buffer += partition[3] * player.DRB3
        buffer += partition[4] * player.DRB4
        buffer += partition[5] * player.DRB5
        buffer += partition[6] * player.DRB6
        buffer += partition[7] * player.DRB7
        buffer += partition[8] * player.DRB8
        buffer += partition[9] * player.DRB9
        mean_data.update({'DRB': buffer})
        #TOV
        buffer = 0.0
        buffer += partition[0] * player.TOV0
        buffer += partition[1] * player.TOV1
        buffer += partition[2] * player.TOV2
        buffer += partition[3] * player.TOV3
        buffer += partition[4] * player.TOV4
        buffer += partition[5] * player.TOV5
        buffer += partition[6] * player.TOV6
        buffer += partition[7] * player.TOV7
        buffer += partition[8] * player.TOV8
        buffer += partition[9] * player.TOV9
        mean_data.update({'TOV': buffer})
        #PF
        buffer = 0.0
        buffer += partition[0] * player.PF0
        buffer += partition[1] * player.PF1
        buffer += partition[2] * player.PF2
        buffer += partition[3] * player.PF3
        buffer += partition[4] * player.PF4
        buffer += partition[5] * player.PF5
        buffer += partition[6] * player.PF6
        buffer += partition[7] * player.PF7
        buffer += partition[8] * player.PF8
        buffer += partition[9] * player.PF9
        mean_data.update({'PF': buffer})
        #plusminus
        buffer = 0.0
        buffer += partition[0] * player.plusminus0
        buffer += partition[1] * player.plusminus1
        buffer += partition[2] * player.plusminus2
        buffer += partition[3] * player.plusminus3
        buffer += partition[4] * player.plusminus4
        buffer += partition[5] * player.plusminus5
        buffer += partition[6] * player.plusminus6
        buffer += partition[7] * player.plusminus7
        buffer += partition[8] * player.plusminus8
        buffer += partition[9] * player.plusminus9
        mean_data.update({'plusminus': buffer})
        #aPER
        buffer = 0.0
        buffer += partition[0] * player.aPER0
        buffer += partition[1] * player.aPER1
        buffer += partition[2] * player.aPER2
        buffer += partition[3] * player.aPER3
        buffer += partition[4] * player.aPER4
        buffer += partition[5] * player.aPER5
        buffer += partition[6] * player.aPER6
        buffer += partition[7] * player.aPER7
        buffer += partition[8] * player.aPER8
        buffer += partition[9] * player.aPER9
        mean_data.update({'aPER': buffer})
        #PER
        buffer = 0.0
        buffer += partition[0] * player.PER0
        buffer += partition[1] * player.PER1
        buffer += partition[2] * player.PER2
        buffer += partition[3] * player.PER3
        buffer += partition[4] * player.PER4
        buffer += partition[5] * player.PER5
        buffer += partition[6] * player.PER6
        buffer += partition[7] * player.PER7
        buffer += partition[8] * player.PER8
        buffer += partition[9] * player.PER9
        mean_data.update({'PER': buffer})
        #EFF
        buffer = 0.0
        buffer += partition[0] * player.EFF0
        buffer += partition[1] * player.EFF1
        buffer += partition[2] * player.EFF2
        buffer += partition[3] * player.EFF3
        buffer += partition[4] * player.EFF4
        buffer += partition[5] * player.EFF5
        buffer += partition[6] * player.EFF6
        buffer += partition[7] * player.EFF7
        buffer += partition[8] * player.EFF8
        buffer += partition[9] * player.EFF9
        mean_data.update({'EFF': buffer})

        plot_list = []
        aaa = ['PTS','FG%','FT%','TP%','AST','STL','BLK','ORB','DRB','TOV','PER']
        try:
            plot_list.append(round((mean_data['PTS']/playermean.PTS)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round(((mean_data['FGM']/mean_data['FGA'])/(playermean.FGM/playermean.FGA))*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round(((mean_data['FTM']/mean_data['FTA'])/(playermean.FTM/playermean.FTA))*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round(((mean_data['TPM']/mean_data['TPA'])/(playermean.TPM/playermean.TPA))*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round((mean_data['AST']/playermean.AST)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round((mean_data['STL']/playermean.STL)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round((mean_data['BLK']/playermean.BLK)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round((mean_data['ORB']/playermean.ORB)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round((mean_data['DRB']/playermean.DRB)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round((mean_data['TOV']/playermean.TOV)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        try:
            plot_list.append(round((mean_data['PER']/playermean.PER)*100,2))
        except ZeroDivisionError:
            plot_list.append(0.0)
        plot_mom_list.append(plot_list)
    conn.dispose()

    return plot_mom_list[0]
