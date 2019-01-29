# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 16:14:25 2019
purpose: plot the csv data
@author: BT
"""
import os
import sys
import csv
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# described nbaplayer class
import nba_players_class

###############################################################################
#read the history information
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
###############################################################################
#plot
name_plot = ['James-Harden','Terry-Rozier','Kyrie-Irving','Gordon-Hayward']
plt.figure()
plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[0]].plusminus)), label=name_plot[0])
plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[1]].plusminus)), label=name_plot[1])
plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[2]].plusminus)), label=name_plot[2])
plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[3]].plusminus)), label=name_plot[3])
plt.ylabel('EFF')
plt.xlabel('Game')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()
#name_plot = ['James-Harden','Terry-Rozier','Kyrie-Irving','Gordon-Hayward']
#plt.figure(figsize=(6,8))
#plt.subplot(4,1,1)
#plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[0]].plusminus)), label=name_plot[0])
#plt.title(name_plot[0])
#plt.ylabel('EFF')
#
#plt.subplot(4,1,2)
#plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[1]].plusminus)), label=name_plot[1])
#plt.title(name_plot[1])
#plt.ylabel('EFF')
#
#plt.subplot(4,1,3)
#plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[2]].plusminus)), label=name_plot[2])
#plt.title(name_plot[2])
#plt.ylabel('EFF')
#
#plt.subplot(4,1,4)
#plt.plot(range(1,11),list(map(int, objplayer_dict[name_plot[3]].plusminus)), label=name_plot[3])
#plt.title(name_plot[3])
#plt.xlabel('game')
#plt.ylabel('EFF')
#
#plt.subplots_adjust(wspace =0.2, hspace =0.45)
#plt.show()
    
    

