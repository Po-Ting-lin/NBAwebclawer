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
#import datetime

class nbaplayer(object):
    '''Each object represents a NBA player,and their plus minus record'''
    def __init__(self,name):
        self.name = name
        self.plusminus = [0]*10
    def update_pm(self,new_pm):
        self.plusminus.pop(-1)
        self.plusminus.insert(0,new_pm)
    def refresh(self,list_pm):
        self.plusminus = list_pm
    def all_setto_zeros(self):
        self.plusminus = [0]*10

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
                temp.refresh(r[1:])    #r[1:] is pm_list
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
    objplayer_dict['date'].update_pm(date)
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
        #find Efficiency
        pm = re.search('"showPlusMinus">.\w*</td>',i).group()
        if (pm):
            pm_list.append(pm.rpartition('"showPlusMinus">')[2].rpartition('</td>')[0])
        else:
            pm_list.append('N/A')
    #combine name and EFF
    #check that the name_list are corresponded to the pm_list
    if len(name_list) != len(pm_list):
        print(url_list[k])
        sys.exit("name_list and pm_list not match!")
    #bulid the dict of object
    for n,p in zip(name_list,pm_list):
        temp = nbaplayer(n)
        temp.update_pm(p)
        #if not data, updata the dict into pool
        if n not in objplayer_dict:
            objplayer_dict.update({str(n):temp})
        #if data already exist, find the obj and updata_pm
        else:
            objplayer_dict[n].update_pm(p)
print('...finish and save all nba player data...')

###############################################################################
#update the CSV information
with open('nba.csv','w', newline='') as file:
    w = csv.writer(file)
    for i in objplayer_dict:
        row = [objplayer_dict[i].name] + objplayer_dict[i].plusminus
        w.writerow(row)
###############################################################################

