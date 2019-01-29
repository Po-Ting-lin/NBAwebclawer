# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 10:37:17 2019

@author: BT
"""
import os
import sys
import csv
import nba_players_class

###############################################################################
#read history information
if os.path.exists('nba.csv'):
    with open('nba.csv', newline='') as file:
        objplayer_dict = dict()
        row = csv.reader(file)
        try:
            for r in row:
                #bulid the dict of object
                temp = nba_players_class.nbaplayer(r[0]) #r[0] is name
                temp.open_csv_refresh_data(r[1:])    #r[1:] is list_coming
                objplayer_dict.update({r[0]:temp})
        except:
            sys.exit("Cannot read nba.csv!")
else:
    sys.exit("Cannot find nba.csv!")
#read team and league data 
if os.path.exists('team.csv'):
    with open('team.csv', newline='') as file:
        row = csv.reader(file)
        count = 0
        try:
            team_lib = []
            for r in row:
                if count == 0:
                    league_data = r
                else:
                    team_lib.append(r)
                count += 1
        except:
            sys.exit("Cannot read team.csv!")
else:
    sys.exit("Cannot find team.csv!")
###############################################################################
team_dict = {'ATL':0,'BKN':1,'BOS':2,'CHA':3,'CHI':4,'CLE':5,'DAL':6,'DEN':7,'DET':8,'GSW':9,'HOU':10,'IND':11,'LAC':12,'LAL':13,'MEM':14,'MIA':15,'MIL':16,'MIN':17,'NOP':18,'NYK':19,'OKC':20,'ORL':21,'PHI':22,'PHX':23,'POR':24,'SAC':25,'SAS':26,'TOR':27,'UTA':28,'WAS':29}

#calculate EFF and PER
for name,player_obj in objplayer_dict.items():
    #find team data ####str
    if name != 'date':
        team_data = team_lib[team_dict[player_obj.team]][0:8]
        opp_data = team_lib[team_dict[player_obj.team]][8:16]
        #calculate PER
        player_obj.advanced_data()
        player_obj.per(team_data,opp_data,league_data)


