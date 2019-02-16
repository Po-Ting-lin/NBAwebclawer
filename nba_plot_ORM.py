# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 18:55:08 2019
purpose: visualize the data
@author: BT
"""
import sys
import random
import numpy as np
import matplotlib.pyplot as plt
from nba_players_class import SCRAPPING,TEAM_TABLE,LEAGUE_TABLE,NBASTORAGE,PLAYER_MEAN_TABLE


scrape = SCRAPPING()
conn,session = scrape.call_session()

#no need to commit()
aa = session.query(NBASTORAGE)
###############################################################################
#sum up
a = aa.all()
############################################################################### 
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")   
print("How about ",a[random.randint(0,len(a)-1)].playersname," , he is a good player!")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~") 
##############################################################################
playermean = session.query(PLAYER_MEAN_TABLE).first()

#input player to be a list
player_list = []
add = 'y'

while (add == 'y'):
    search = []
    while (len(search) != 1):
        input_player = input("Input players:")
        search = []
        for player in aa.all():
            if input_player in player.playersname:
                search.append(player)
                print(player.playersname)
        if len(search) == 0:
            print("No such player named ",input_player)    
        print('\n\n\n')
    player_list.append(search[0])
    add = input("Add player?")


print('player_list including: ')
for i in player_list:
    print(i.playersname)

plot_mom_list = []
for player in player_list:
    this_player_totaltime = 0
    for game in range(10):
        exec("this_player_totaltime += player.ontime"+str(game))
    #ontime of each player in each game ratio
    partition = [0]*10
    aaaa = ['ontime','PTS','AST','STL','BLK','FGA','FGM','FTA','FTM','TPA','TPM','ORB','DRB','TOV','PF','plusminus','aPER','PER','EFF']
    for game in range(10):
        exec("partition["+str(game)+"] = (player.ontime"+str(game)+"/this_player_totaltime)")
    mean_data = dict()
    for col in aaaa:
        buffer = 0.0
        for game in range(10):
            exec("buffer += partition["+str(game)+"]*player."+col+str(game))
        mean_data.update({col: buffer})
    plot_list = dict()
    aaa = ['PTS','FG%','FT%','TP%','AST','STL','BLK','ORB','DRB','TOV','PER']
    try:
        plot_list.update({'PTS': round((mean_data['PTS']/playermean.PTS)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'PTS': 0.0})
    try:
        plot_list.update({'FG%': round(((mean_data['FGM']/mean_data['FGA'])/(playermean.FGM/playermean.FGA))*100,2)})
    except ZeroDivisionError:
        plot_list.update({'FG%': 0.0})
    try:
        plot_list.update({'FT%': round(((mean_data['FTM']/mean_data['FTA'])/(playermean.FTM/playermean.FTA))*100,2)})
    except ZeroDivisionError:
        plot_list.update({'FT%': 0.0})
    try:
        plot_list.update({'TP%': round(((mean_data['TPM']/mean_data['TPA'])/(playermean.TPM/playermean.TPA))*100,2)})
    except ZeroDivisionError:
        plot_list.update({'TP%': 0.0})
    try:
        plot_list.update({'AST': round((mean_data['AST']/playermean.AST)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'AST': 0.0})
    try:
        plot_list.update({'STL': round((mean_data['STL']/playermean.STL)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'STL': 0.0})
    try:
        plot_list.update({'BLK': round((mean_data['BLK']/playermean.BLK)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'BLK': 0.0})
    try:
        plot_list.update({'ORB': round((mean_data['ORB']/playermean.ORB)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'ORB': 0.0})
    try:
        plot_list.update({'DRB': round((mean_data['DRB']/playermean.DRB)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'DRB': 0.0})
    try:
        plot_list.update({'TOV': round((mean_data['TOV']/playermean.TOV)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'TOV': 0.0})
    try:
        plot_list.update({'PER': round((mean_data['PER']/playermean.PER)*100,2)})
    except ZeroDivisionError:
        plot_list.update({'PER': 0.0})
    plot_mom_list.append(plot_list)


col_count = len(plot_mom_list)
bar_width = 0.05
index = np.arange(col_count)
#alpha is transparency%
alpha = 0.6
f, ax = plt.subplots(figsize=(10,5))
A = plt.bar(index,[plot_mom_list[x]['PTS'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="PTS")
B = plt.bar(index+0.05,[plot_mom_list[x]['FG%'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="FG%") 
C = plt.bar(index+0.1,[plot_mom_list[x]['FT%'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="FT%") 
D = plt.bar(index+0.15,[plot_mom_list[x]['TP%'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="TP%")
E = plt.bar(index+0.2,[plot_mom_list[x]['AST'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="AST")
F = plt.bar(index+0.25,[plot_mom_list[x]['STL'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="STL")
G = plt.bar(index+0.3,[plot_mom_list[x]['BLK'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="BLK")
H = plt.bar(index+0.35,[plot_mom_list[x]['ORB'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="ORB")
I = plt.bar(index+0.4,[plot_mom_list[x]['DRB'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="DRB")
J = plt.bar(index+0.45,[plot_mom_list[x]['TOV'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="TOV")
K = plt.bar(index+0.5,[plot_mom_list[x]['PER'] for x in range(len(plot_mom_list))],bar_width,alpha=alpha,label="PER")
plt.ylabel("Percentage In League(%)")
plt.xlabel("Player(s)")
plt.ylim(-10,400)
plt.title("Players' data in recent 10 games")

plt.xticks(index+0.25 ,tuple([player_list[i].playersname for i in range(len(player_list))]))
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True)
plt.show()


#
##PER
#plt.figure()
#for player in aa.limit(15).all():
#    xline = [i for i in range(1,11)]
#    yline = [player.PER0,player.PER1,player.PER2,player.PER3,player.PER4,player.PER5,player.PER6,player.PER7,player.PER8,player.PER9]
#    plt.plot(xline,yline,label=player.playersname)
#plt.title('PER in recent 10 games')
#plt.xlabel('game')
#plt.ylabel('PER')
#plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.show()
#
##EFF histogram
#EFF_list = []
#for player in aa.all():
#    EFF_list.append(player.EFF0)
#plt.hist(EFF_list,bins=30)
#plt.title('Distribution of EFF')
#plt.ylabel('number of players')
#plt.xlabel('EFF')
#plt.show()
#
##PER histogram
#PER_list = []
#for player in aa.all():
#    PER_list.append(player.PER0)
#plt.hist(PER_list,bins=30)
#plt.title('Distribution of PER')
#plt.ylabel('number of players')
#plt.xlabel('PER')
#plt.show()


session.commit()
conn.dispose()