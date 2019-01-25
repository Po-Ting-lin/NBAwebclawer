# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 23:43:57 2018
purpose: nba box scraping
@author: BT
"""
import re
import os
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import time

class nbaplayer(object):
    '''Each object represents a NBA player,and their plus minus record'''
    def __init__(self,name):
        self.name = name
        self.plusminus = [0]*10
        self.ontime = [0]*10
        self.score = [0]*10
        self.off_rebounds = [0]*10
        self.def_rebounds = [0]*10
        self.assists = [0]*10
        self.steals = [0]*10
        self.blocks = [0]*10
        self.fgm = [0]*10
        self.fga = [0]*10
        self.tpm = [0]*10
        self.tpa = [0]*10
        self.ftm = [0]*10
        self.fta = [0]*10
        self.turnovers = [0]*10
        
    def update_all(self,pm,ontime,score,off_rebounds,def_rebounds,assists,steals,blocks,fgm,fga,tpm,tpa,ftm,fta,turnovers):
        self.plusminus.pop(-1)
        self.plusminus.insert(0,pm)
        self.ontime.pop(-1)
        self.ontime.insert(0,ontime)
        self.score.pop(-1)
        self.score.insert(0,score)
        self.off_rebounds.pop(-1)
        self.off_rebounds.insert(0,off_rebounds)
        self.def_rebounds.pop(-1)
        self.def_rebounds.insert(0,def_rebounds)
        self.assists.pop(-1)
        self.assists.insert(0,assists)
        self.steals.pop(-1)
        self.steals.insert(0,steals)
        self.blocks.pop(-1)
        self.blocks.insert(0,blocks)
        self.fgm.pop(-1)
        self.fgm.insert(0,fgm)
        self.fga.pop(-1)
        self.fga.insert(0,fga)
        self.tpm.pop(-1)
        self.tpm.insert(0,tpm)
        self.tpa.pop(-1)
        self.tpa.insert(0,tpa)
        self.ftm.pop(-1)
        self.ftm.insert(0,ftm)
        self.fta.pop(-1)
        self.fta.insert(0,fta)
        self.turnovers.pop(-1)
        self.turnovers.insert(0,turnovers)
        
    def open_csv_refresh_data(self,list_coming):
        self.plusminus = list_coming[0:10]
        self.ontime = list_coming[10:20]
        self.score = list_coming[20:30]
        self.off_rebounds = list_coming[30:40]
        self.def_rebounds = list_coming[40:50]
        self.assists = list_coming[50:60]
        self.steals = list_coming[60:70]
        self.blocks = list_coming[70:80]
        self.fgm = list_coming[80:90]
        self.fga = list_coming[90:100]
        self.tpm = list_coming[100:110]
        self.tpa = list_coming[110:120]
        self.ftm = list_coming[120:130]
        self.fta = list_coming[130:140]
        self.turnovers = list_coming[140:150]
    
    def update_date(self,date):
        self.plusminus.pop(-1)
        self.plusminus.insert(0,date)
        
    def all_setto_zeros(self):
        self.plusminus = [0]*10


def find_number(i,target_text,number_list):
    '''Find data_number in text of each player and append it to data_list (target must include "> and <)'''
    target_text_1 = target_text.rpartition('">')[0]+target_text.rpartition('">')[1]
    target_text_2 = target_text.rpartition('<')[1]+target_text.rpartition('<')[2]
    num = re.search(target_text,i).group()
    if (num):
        number_list.append(num.rpartition(target_text_1)[2].rpartition(target_text_2)[0])
    else:
        number_list.append('0')
    return number_list


def get_page_text(url):
    '''A way to get url html text'''
    #set web surfer close
    chrome_option = Options()
    chrome_option.add_argument("--headless")
    chromedriver = r"C:\Users\BT\AppData\Local\Programs\Python\Python37-32\Scripts\chromedriver.exe"
    #call automatic control
    try:
        driver =  webdriver.Chrome(chromedriver,chrome_options=chrome_option)
    except:
        print('cannot open webdriver!')
        return 0
    #URL
    driver.get(url)
    #get HTML source
    text = driver.page_source
    driver.close()
    return text
###############################################################################
#read the history information
if os.path.exists('nba.csv'):
    with open('nba.csv', newline='') as file:
        objplayer_dict = dict()
        row = csv.reader(file)
        try:
            for r in row:
                #bulid the dict of object
                temp = nbaplayer(r[0]) #r[0] is name
                temp.open_csv_refresh_data(r[1:])    #r[1:] is list_coming
                objplayer_dict.update({r[0]:temp})
        except:
            sys.exit("Cannot read nba.csv!")
else:
    sys.exit("Cannot find nba.csv!")
###############################################################################
#nba taiwan website
url = 'https://tw.global.nba.com/scores/'
main_text = get_page_text(url)
soup = BeautifulSoup(main_text,'html.parser')
#check date
date = soup.find('span','day ng-binding').string
date = date.split('月')[0].strip(' ') + date.split('月')[1].split('日')[0].strip(' ')
for i in range(len(objplayer_dict['date'].plusminus)):
    if objplayer_dict['date'].plusminus[i] == date:
        sys.exit("this page has already recorded!")
    else:
        pass
else:
    objplayer_dict['date'].update_date(date)
#find each post
post = soup.find_all('div',class_="row snapshot-content")
url_list= []
for i in post:
    try:
        post_url = str(i.find('a',class_="sib3-game-url stats-boxscore game-status-3")['href'])
        enter = 'https://tw.global.nba.com' + post_url
        if post_url:
            url_list.append(enter)
    except:
        print('none')

#find the information from each game 
for k in range(len(url_list)):
    name_list = []
    ontime_list = []
    
    score_list = []
    off_rebounds_list = []
    def_rebounds_list = []
    assists_list = []
    steals_list = []
    blocks_list = []
    fgm_list = []
    fga_list = []
    tpm_list = []
    tpa_list = []
    ftm_list = []
    fta_list = []
    turnovers_list = []
    
    pm_list = []
    new_player = []
    print('Start searching the information in \n'+ url_list[k])
    
    #iteratively getting the text
    status = True
    count = 0
    while(status):
        post_maintext = get_page_text(url_list[k])
        time.sleep(0.8)
        #find the text per player from each game
        player = post_maintext.split('<tr data-ng-repeat="playerGameStats in teamData.gamePlayers')
        if len(player) <= 2:
            print('cannot get the text from page ' + url_list[k])
            count += 1
            if count > 10:
                sys.exit("cannot get this page")
            print('...retry...')
        else:
            status = False
    
    #access the text of this page
    for i in player:
        #data cleaning
        if ("showPlusMinus" in i) and(not bool(re.match('" class',i))):
            new_player.append(i)
    new_player.pop(0)
    #find name and plusminus per player from the text
    for i in new_player:
        #find name
        a = i.rpartition('firstName" class="ng-binding">')[2].rpartition('</span><span data-ng-show="playerGameStats.profile.firstName" class=""><span data-ng-i18next="delimiter.firstNameLastName">-</span></span><span data-ng-bind-html="playerGameStats.profile.lastName" class="ng-binding">')
        first = a[0]
        last = a[2].rpartition('</span>')[0]
        if 'Nene' in i:
            b = a
        if (first) and (last):
            name_list.append(first+'-'+last)
        elif (first): 
            name_list.append(first)
        elif (last): #Nene
            last = a[2].rpartition('</span><span data-ng-show="playerGameStats.profile.firstName" class="ng-hide"><span data-ng-i18next="delimiter.firstNameLastName">-</span></span><span data-ng-bind-html="playerGameStats.profile.lastName" class="ng-binding">')[2].rpartition('</span>')[0]
            name_list.append(last)
        else:
            name_list.append('N/A')
        
        #find data(15)
        #find ontime
        ontime_list = find_number(i,'statTotal.secs">.\w*:.\w*</td>',ontime_list)
        #find plusminus
        pm_list = find_number(i,'"showPlusMinus">.\w*</td>',pm_list)
        #find score
        score_list = find_number(i,'statTotal.points">.\w*</td>',score_list)
        #find off_rebounds
        off_rebounds_list = find_number(i,'statTotal.offRebs">.\w*</td>',off_rebounds_list)
        #find def_rebounds
        def_rebounds_list = find_number(i,'statTotal.defRebs">.\w*</td>',def_rebounds_list)
        #find assists
        assists_list = find_number(i,'statTotal.assists">.\w*</td>',assists_list)
        #find steals
        steals_list = find_number(i,'statTotal.steals">.\w*</td>',steals_list)
        #find blocks
        blocks_list = find_number(i,'statTotal.blocks">.\w*</td>',blocks_list)
        #find fgm
        fgm_list = find_number(i,'statTotal.fgm">.\w*</td>',fgm_list)
        #find fga
        fga_list = find_number(i,'statTotal.fga">.\w*</td>',fga_list)
        #find tpm
        tpm_list = find_number(i,'statTotal.tpm">.\w*</td>',tpm_list)
        #find tpa
        tpa_list = find_number(i,'statTotal.tpa">.\w*</td>',tpa_list)
        #find ftm
        ftm_list = find_number(i,'statTotal.ftm">.\w*</td>',ftm_list)        
        #find fta
        fta_list = find_number(i,'statTotal.fta">.\w*</td>',fta_list)
        #find turnovers
        turnovers_list = find_number(i,'statTotal.turnovers">.\w*</td>',turnovers_list)
       
    #combine name and plusminus
    #check that the name_list are corresponded to the pm_list
    if len(name_list) != (len(ontime_list)+len(pm_list)+len(score_list)+len(off_rebounds_list)+len(def_rebounds_list)+len(assists_list)+len(steals_list)+len(blocks_list)+len(fgm_list)+len(fga_list)+len(tpm_list)+len(tpa_list)+len(ftm_list)+len(fta_list)+len(turnovers_list))/15:
        print('This URL ',url_list[k])
        sys.exit("len of lists not match!")
        
    #bulid the dict of object
    zip_injection = zip(name_list,pm_list,ontime_list,score_list,off_rebounds_list,def_rebounds_list,assists_list,steals_list,blocks_list,fgm_list,fga_list,tpm_list,tpa_list,ftm_list,fta_list,turnovers_list)
    for name,pm,ontime,score,off_rebounds,def_rebounds,assists,steals,blocks,fgm,fga,tpm,tpa,ftm,fta,turnovers in zip_injection:
        #create nbaplayer object temporarily
        temp = nbaplayer(name)
        temp.update_all(pm,ontime,score,off_rebounds,def_rebounds,assists,steals,blocks,fgm,fga,tpm,tpa,ftm,fta,turnovers)
        #if not data, updata the dict into pool
        #( n is scrapping data, objplayer_dict is historical data. )
        if name not in objplayer_dict:
            objplayer_dict.update({str(name):temp})
        #if n already exist, find the obj and updata_pm
        else:
            objplayer_dict[name].update_all(pm,ontime,score,off_rebounds,def_rebounds,assists,steals,blocks,fgm,fga,tpm,tpa,ftm,fta,turnovers)
print('...finish and save all nba player data...')

###############################################################################
#update the CSV information
with open('nba.csv','w', newline='') as file:
    w = csv.writer(file)
    for i in objplayer_dict:
        row = [objplayer_dict[i].name] + objplayer_dict[i].plusminus+ objplayer_dict[i].ontime+ objplayer_dict[i].score+ objplayer_dict[i].off_rebounds+ objplayer_dict[i].def_rebounds+ objplayer_dict[i].assists+ objplayer_dict[i].steals+ objplayer_dict[i].blocks+ objplayer_dict[i].fgm+ objplayer_dict[i].fga+ objplayer_dict[i].tpm+ objplayer_dict[i].tpa+ objplayer_dict[i].ftm+ objplayer_dict[i].fta+ objplayer_dict[i].turnovers
        w.writerow(row)
###############################################################################



