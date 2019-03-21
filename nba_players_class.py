# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:04:59 2019

@author: BT
"""
import sys
import re
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String,Float,Integer


###############################################################################

def find_number(i, target_text, number_list, ontime_bool=False):
    """ Find data_number in text of each player and append it to data_list (target must include "> and <) """

    target_text_1 = target_text.rpartition('">')[0]+target_text.rpartition('">')[1]
    target_text_2 = target_text.rpartition('<')[1]+target_text.rpartition('<')[2]
    num = re.search(target_text, i).group()
    if num:
        into = num.rpartition(target_text_1)[2].rpartition(target_text_2)[0]
        if ontime_bool:
            into = int(into.split(':')[0]) + round(int(into.split(':')[1])/60, 2)
        number_list.append(into)
    else:
        number_list.append('0')
    if not ontime_bool:
        number_list = list(map(float, number_list))
    return number_list
        
        
class TEXT(object):
    def __init__(self,url):
        self.url = url

    def get_page_text(self):
        """A way to get url html text"""
        # set web surfer close
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        chromedriver = r"/usr/bin/chromedriver"
        # call automatic control
        try:
            driver =  webdriver.Chrome(chromedriver,chrome_options=chrome_option)
        except:
            print('cannot open webdriver!')
            return 0
        # URL
        driver.get(self.url)
        # get HTML source
        text = driver.page_source
        driver.close()
        return text


class LEAGUE(object):  # require class TEXT
    """purpose: to get lgAST,lgFGM,lgFTM,lgPTS,lgFGA,lgORB,lgDRB,lgTO,lgFTA,lgPF,lgPace,lgPER"""

    def find_league_statistics(self):
        url = "https://www.basketball-reference.com/leagues/NBA_stats.html"
        main_text = TEXT(url).get_page_text()
        soup = BeautifulSoup(main_text,'html.parser')
        a = soup.find_all("tr",attrs={"data-row": "0"})
        league_data = []
        mark = ['fg_per_g','fga_per_g','ft_per_g','fta_per_g','pts_per_g','ast_per_g','orb_per_g','drb_per_g','tov_per_g','pf_per_g','pace']
        for i in a:
            ii = str(i)
            if 'age' in ii:
                for j in mark:
                    league_data.append(i.find("td",attrs={"data-stat": j}).string)
            else:
                continue
        # Player Efficiency Rating (PER) 2018-2019 League average: 15.0
        league_data.append('15.0')
        return league_data


class TEAM(object):  # require class TEXT
    """purpose: to get tmMP,tmAST,tmFGM,tmFGA,tmFTA,tmORB,tmDRB,tmTO,oppDRB,oppFGA,oppFGM,oppFTA,oppORB,oppTO"""
    def __init__(self):
        self.team = 'TOR'

    def find_team_statistics(self,team):
        url = "https://www.basketball-reference.com/teams/" + team + "/2019.html"
        main_text = TEXT(url).get_page_text()
        soup = BeautifulSoup(main_text,'html.parser')
        a = soup.find_all("tr")
        team_data = []
        opp_data = []
        mark = ['mp_per_g', 'ast_per_g', 'fg_per_g', 'fga_per_g', 'fta_per_g', 'orb_per_g', 'drb_per_g', 'tov_per_g']
        mark_opp = ['mp_per_g']+['opp_'+x for x in mark[1:]]
        for i in a:
            ii = str(i)
            if ('Team/G' in ii) and ('mp_per_g' in ii):
                for j in mark:
                    team_data.append(i.find("td",attrs={"data-stat": j}).string)
            elif ('Opponent/G' in ii) and ('mp_per_g' in ii):
                for j in mark_opp:
                    opp_data.append(i.find("td",attrs={"data-stat": j}).string)
            else:
                continue
        return team_data, opp_data

# father
class Base_of(object):
    def __init__(self):
        self.sess = None
        self.conn = None
        
    def call_session(self,call_who='localhost'):
        # read nba player's data, team data, and league data
        # engine = create_engine('mysql+pymysql://<USER>:<PASSWORD>@127.0.0.1/<DATABASE>')

        # connection in local mySQL
        self.conn = create_engine('mysql+pymysql://root:root@localhost/nba_db',poolclass=NullPool)

        # connection by cloud SQL proxy
        # conn = create_engine('mysql+pymysql://root:root@127.0.0.1:3309/nba_cloud', poolclass=NullPool)

        # set long timeout
        # conn.execute('SET GLOBAL innodb_lock_wait_timeout = 10000;')
        # conn.execute('SET innodb_lock_wait_timeout = 10000;')

        # session:(connection object that communicating ORM with SQL)
        Session = sessionmaker(bind=self.conn, autoflush=False)
        self.sess = Session()
        return self.conn,self.sess
    
    def update(self, name, property, new_value):
        for i in range(8,-1,-1):
            exec("self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == "+ name +").update({NBASTORAGE."+property+str(i+1)+": NBASTORAGE."+property+str(i)+"})")
        exec("self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == "+ name +").update({NBASTORAGE."+property+"0: float("+new_value+")})")

        return
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime9: NBASTORAGE.ontime8})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime8: NBASTORAGE.ontime7})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime7: NBASTORAGE.ontime6})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime6: NBASTORAGE.ontime5})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime5: NBASTORAGE.ontime4})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime4: NBASTORAGE.ontime3})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime3: NBASTORAGE.ontime2})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime2: NBASTORAGE.ontime1})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime1: NBASTORAGE.ontime0})
        # session_scrape.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime0: float(ontime)})

# a child of Base_of
class SCRAPPING(Base_of):
    def __init__(self):
        self.date = '0/0'
        self.soup = None
        super().__init__()

    def call_soup(self,main_text):
        """main_text is for the main page"""
        self.soup = BeautifulSoup(main_text, 'html.parser')
        return self.soup

    def check_date(self):
        date = self.soup.find('span', 'day ng-binding').string
        date_scrapped = date.split('月')[0].strip(' ') + '/' + date.split('月')[1].split('日')[0].strip(' ')
        status = True
        try:
            # find record_date
            record_date = self.sess.query(DATE_TABLE).first().date0
        except Exception:
            # no obj in query, create a new one
            print('create a new date obj...')
            record_date = '0/0'
            tem = DATE_TABLE('today',['0/0']*10)
            self.sess.add(tem)
            # stop below code
            status = False
            
        if (record_date != date_scrapped) and (status == True):
            # the obj is exist, but today is not been recorded.
            aa = self.sess.query(DATE_TABLE)
            a = aa.first()
            date_list = [a.date0,a.date1,a.date2,a.date3,a.date4,a.date5,a.date6,a.date7,a.date8,a.date9]
            date_list.pop(-1)
            date_list.insert(0,date_scrapped)
            aa.update({DATE_TABLE.date0: date_list[0]})
            aa.update({DATE_TABLE.date1: date_list[1]})
            aa.update({DATE_TABLE.date2: date_list[2]})
            aa.update({DATE_TABLE.date3: date_list[3]})
            aa.update({DATE_TABLE.date4: date_list[4]})
            aa.update({DATE_TABLE.date5: date_list[5]})
            aa.update({DATE_TABLE.date6: date_list[6]})
            aa.update({DATE_TABLE.date7: date_list[7]})
            aa.update({DATE_TABLE.date8: date_list[8]})
            aa.update({DATE_TABLE.date9: date_list[9]})
        elif (record_date == date_scrapped) and (status == True):
            # if this page has already recorded,this code shut down
            sys.exit("this page has already recorded!")
        elif (status == False):
            # create a new object and skip the updating process
            print('skip updating date...')
        return self.sess

    def clean_date0(self):
        aa = self.sess.query(DATE_TABLE)
        aa.update({DATE_TABLE.date0: '0/0'})
        return self.sess
    
    def find_each_post(self):
        post = self.soup.find_all('div', class_="row snapshot-content")
        url_list = []
        for i in post:
            try:
                post_url = str(i.find('a', class_="sib3-game-url stats-boxscore game-status-3")['href'])
                enter = 'https://tw.global.nba.com' + post_url
                if post_url:
                    url_list.append(enter)
            except:
                print('none')
        return url_list

    def mean_of_each_player_analysis(self):
        """calculate the average of each data by considering the proportion of ontime of each player"""

        # scrape = SCRAPPING()
        # conn, session = scrape.call_session()
        player_list = self.sess.query(NBASTORAGE).all()
        playermean = self.sess.query(PLAYER_MEAN_TABLE).filter(PLAYER_MEAN_TABLE.name == 'mean').first()

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

            # ontime of each player in each game ratio
            partition = [0] * 10
            aaaa = ['ontime', 'PTS', 'AST', 'STL', 'BLK', 'FGA', 'FGM', 'FTA', 'FTM', 'TPA', 'TPM', 'ORB', 'DRB', 'TOV',
                    'PF', 'plusminus', 'aPER', 'PER', 'EFF']
            if this_player_totaltime == 0:
                partition = [0] * 10
            else:
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

            # ontime
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
            # PTS
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
            # AST
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
            # STL
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
            # BLK
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
            # FGA
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
            # FGM
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
            # FTA
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
            # FTM
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
            # TPA
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
            # TPM
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
            # ORB
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
            # DRB
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
            # TOV
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
            # PF
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
            # plusminus
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
            # aPER
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
            # PER
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
            # EFF
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

            # update PLAYER_MEAN_TABLE
            eachplayermean = self.sess.query(PLAYER_MEAN_TABLE)
            dumplist = []
            aaa = ['PTS', 'FG%', 'FT%', 'TP%', 'AST', 'STL', 'BLK', 'ORB', 'DRB', 'TOV', 'PER']
            try:
                dumplist.append(round((mean_data['PTS'] / playermean.PTS) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(
                    round(((mean_data['FGM'] / mean_data['FGA']) / (playermean.FGM / playermean.FGA)) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(
                    round(((mean_data['FTM'] / mean_data['FTA']) / (playermean.FTM / playermean.FTA)) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(
                    round(((mean_data['TPM'] / mean_data['TPA']) / (playermean.TPM / playermean.TPA)) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(round((mean_data['AST'] / playermean.AST) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(round((mean_data['STL'] / playermean.STL) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(round((mean_data['BLK'] / playermean.BLK) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(round((mean_data['ORB'] / playermean.ORB) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(round((mean_data['DRB'] / playermean.DRB) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(round((mean_data['TOV'] / playermean.TOV) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            try:
                dumplist.append(round((mean_data['PER'] / playermean.PER) * 100, 2))
            except ZeroDivisionError:
                dumplist.append(0.0)
            # update session
            # FG% --> FGM
            # FT% --> FTM
            # TP% --> TPM

            #no such player
            if not self.sess.query(PLAYER_MEAN_TABLE).filter(PLAYER_MEAN_TABLE.name == player.playersname).first():
                tem = PLAYER_MEAN_TABLE(player.playersname, 0, dumplist[0], dumplist[4], dumplist[5], dumplist[6], 0, dumplist[1], 0, dumplist[2], 0, dumplist[3], dumplist[7], dumplist[8], dumplist[9], 0, 0, 0, dumplist[10], 0)
                self.sess.add(tem)
            else:
                pl = self.sess.query(PLAYER_MEAN_TABLE).filter(PLAYER_MEAN_TABLE.name == player.playersname)
                pl.update({PLAYER_MEAN_TABLE.PTS: dumplist[0]})
                pl.update({PLAYER_MEAN_TABLE.FGM: dumplist[1]})
                pl.update({PLAYER_MEAN_TABLE.FTM: dumplist[2]})
                pl.update({PLAYER_MEAN_TABLE.TPM: dumplist[3]})
                pl.update({PLAYER_MEAN_TABLE.AST: dumplist[4]})
                pl.update({PLAYER_MEAN_TABLE.STL: dumplist[5]})
                pl.update({PLAYER_MEAN_TABLE.BLK: dumplist[6]})
                pl.update({PLAYER_MEAN_TABLE.ORB: dumplist[7]})
                pl.update({PLAYER_MEAN_TABLE.DRB: dumplist[8]})
                pl.update({PLAYER_MEAN_TABLE.TOV: dumplist[9]})
                pl.update({PLAYER_MEAN_TABLE.PER: dumplist[10]})

        return self.sess

    def scrape_player(self):
        """scarpe raw data of each players"""

        # main scrapping
        # nba taiwan website
        url = 'https://tw.global.nba.com/scores/'
        # get main text
        main_text = TEXT(url).get_page_text()
        # call soup for date
        self.call_soup(main_text)
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # clean date0
        self.sess = self.clean_date0()
        # check the date
        self.sess  = self.check_date()
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # find each post
        url_list = self.find_each_post()

        # find the information from each game
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
            fouls_list = []
            pm_list = []
            new_player = []
            print('Start searching the information in \n' + url_list[k])

            # iteratively getting the text
            status = True
            count = 0
            while (status):
                post_maintext = TEXT(url_list[k]).get_page_text()
                time.sleep(0.8)
                # find the text per player from each game
                player = post_maintext.split('<tr data-ng-repeat="playerGameStats in teamData.gamePlayers')
                if len(player) <= 2:
                    print('cannot get the text from page ' + url_list[k])
                    count += 1
                    if count > 10:
                        sys.exit("cannot get this page")
                    print('...retry...')
                else:
                    status = False
            # get each team from this page
            try:
                team1 = re.search('logos/(.+?)_logo.svg', post_maintext.split('team-img')[1]).group(1)
                team2 = re.search('logos/(.+?)_logo.svg', post_maintext.split('team-img')[2]).group(1)
            except:
                sys.exit("cannot find team from this page!")
            # access the text of this page and define team
            k_number = 0
            status_team = team1
            team_list = []
            for i in player:
                # data cleaning
                if ("showPlusMinus" in i) and (not bool(re.match('" class', i))):
                    new_player.append(i)
                    team_list.append(status_team)
                else:
                    if k_number >= 3:
                        status_team = team2
                    k_number += 1
            new_player.pop(0)
            team_list.pop(0)
            # find name and plusminus per player from the text
            for i in new_player:
                # find name
                a = i.rpartition('firstName" class="ng-binding">')[2].rpartition(
                    '</span><span data-ng-show="playerGameStats.profile.firstName" class=""><span data-ng-i18next="delimiter.firstNameLastName">-</span></span><span data-ng-bind-html="playerGameStats.profile.lastName" class="ng-binding">')
                first = a[0]
                last = a[2].rpartition('</span>')[0]
                if 'Nene' in i:
                    b = a
                if (first) and (last):
                    name_list.append(first + '-' + last)
                elif (first):
                    name_list.append(first)
                elif (last):  # Nene
                    last = a[2].rpartition(
                        '</span><span data-ng-show="playerGameStats.profile.firstName" class="ng-hide"><span data-ng-i18next="delimiter.firstNameLastName">-</span></span><span data-ng-bind-html="playerGameStats.profile.lastName" class="ng-binding">')[
                        2].rpartition('</span>')[0]
                    name_list.append(last)
                else:
                    name_list.append('N/A')

                # find data(15)
                # find ontime
                ontime_list = find_number(i, 'statTotal.secs">.\w*:.\w*</td>', ontime_list, ontime_bool=True)
                # find plusminus
                pm_list = find_number(i, '"showPlusMinus">.\w*</td>', pm_list)
                # find score
                score_list = find_number(i, 'statTotal.points">.\w*</td>', score_list)
                # find off_rebounds
                off_rebounds_list = find_number(i, 'statTotal.offRebs">.\w*</td>', off_rebounds_list)
                # find def_rebounds
                def_rebounds_list = find_number(i, 'statTotal.defRebs">.\w*</td>', def_rebounds_list)
                # find assists
                assists_list = find_number(i, 'statTotal.assists">.\w*</td>', assists_list)
                # find steals
                steals_list = find_number(i, 'statTotal.steals">.\w*</td>', steals_list)
                # find blocks
                blocks_list = find_number(i, 'statTotal.blocks">.\w*</td>', blocks_list)
                # find fgm
                fgm_list = find_number(i, 'statTotal.fgm">.\w*</td>', fgm_list)
                # find fga
                fga_list = find_number(i, 'statTotal.fga">.\w*</td>', fga_list)
                # find tpm
                tpm_list = find_number(i, 'statTotal.tpm">.\w*</td>', tpm_list)
                # find tpa
                tpa_list = find_number(i, 'statTotal.tpa">.\w*</td>', tpa_list)
                # find ftm
                ftm_list = find_number(i, 'statTotal.ftm">.\w*</td>', ftm_list)
                # find fta
                fta_list = find_number(i, 'statTotal.fta">.\w*</td>', fta_list)
                # find turnovers
                turnovers_list = find_number(i, 'statTotal.turnovers">.\w*</td>', turnovers_list)
                # find fouls
                fouls_list = find_number(i, '.statTotal.fouls">.\w*</td>', fouls_list)

            # combine name and plusminus
            # check that the name_list are corresponded to the pm_list
            if len(name_list) != (len(ontime_list) + len(pm_list) + len(score_list) + len(off_rebounds_list) + len(
                    def_rebounds_list) + len(assists_list) + len(steals_list) + len(blocks_list) + len(fgm_list) + len(
                    fga_list) + len(tpm_list) + len(tpa_list) + len(ftm_list) + len(fta_list) + len(
                    turnovers_list)) / 15:
                print('This URL ', url_list[k])
                sys.exit("len of lists not match!")

            # update data
            zip_injection = zip(name_list, pm_list, ontime_list, score_list, off_rebounds_list, def_rebounds_list,
                                assists_list, steals_list, blocks_list, fgm_list, fga_list, tpm_list, tpa_list,
                                ftm_list, fta_list, turnovers_list, fouls_list, team_list)
            for name, pm, ontime, score, off_rebounds, def_rebounds, assists, steals, blocks, fgm, fga, tpm, tpa, ftm, fta, turnovers, fouls, team in zip_injection:
                if team == 'CHA':
                    team = 'CHO'
                elif team == 'BKN':
                    team = 'BRK'
                elif team == 'PHX':
                    team = 'PHO'
                if type(ontime) != float:
                    sys.exit("ontime is not float!")
                if (type(name) != str) or (type(team) != str):
                    sys.exit("name or team is not string!")
                if (type(score) != float) or (type(off_rebounds) != float):
                    sys.exit("score or off_rebounds is not float!")
                a = self.sess.query(NBASTORAGE)
                # qeury object
                ep = a.filter(NBASTORAGE.playersname == name)
                # NBASTORAGE object
                ep_obj = ep.first()
                if not ep_obj:
                    # cannot find this player, create a new object
                    tem = NBASTORAGE(name, team, [ontime] + [0.0] * 9, [score] + [0.0] * 9, [off_rebounds] + [0.0] * 9,
                                     [def_rebounds] + [0.0] * 9, [assists] + [0.0] * 9, [steals] + [0.0] * 9,
                                     [blocks] + [0.0] * 9, [fga] + [0.0] * 9, [fgm] + [0.0] * 9, [fta] + [0.0] * 9,
                                     [ftm] + [0.0] * 9, [tpa] + [0.0] * 9, [tpm] + [0.0] * 9, [turnovers] + [0.0] * 9,
                                     [fouls] + [0.0] * 9, [pm] + [0.0] * 9)
                    self.sess.add(tem)

                else:
                    # find it! and update
                    # update each
                    self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                        {NBASTORAGE.team: team})

                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ontime" + str(
                                i + 1) + ": NBASTORAGE.ontime" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.ontime0: float(ontime)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.PTS" + str(
                                i + 1) + ": NBASTORAGE.PTS" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.PTS0: float(score)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.ORB" + str(
                                i + 1) + ": NBASTORAGE.ORB" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.ORB0: float(off_rebounds)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.DRB" + str(
                                i + 1) + ": NBASTORAGE.DRB" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.DRB0: float(def_rebounds)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.AST" + str(
                                i + 1) + ": NBASTORAGE.AST" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.AST0: float(assists)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.STL" + str(
                                i + 1) + ": NBASTORAGE.STL" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.STL0: float(steals)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.BLK" + str(
                                i + 1) + ": NBASTORAGE.BLK" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.BLK0: float(blocks)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.FGA" + str(
                                i + 1) + ": NBASTORAGE.FGA" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.FGA0: float(fga)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.FGM" + str(
                                i + 1) + ": NBASTORAGE.FGM" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.FGM0: float(fgm)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.FTA" + str(
                                i + 1) + ": NBASTORAGE.FTA" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.FTA0: float(fta)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.FTM" + str(
                                i + 1) + ": NBASTORAGE.FTM" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.FTM0: float(ftm)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.TPA" + str(
                                i + 1) + ": NBASTORAGE.TPA" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.TPA0: float(tpa)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.TPM" + str(
                                i + 1) + ": NBASTORAGE.TPM" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.TPM0: float(tpm)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.TOV" + str(
                                i + 1) + ": NBASTORAGE.TOV" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.TOV0: float(turnovers)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.PF" + str(
                                i + 1) + ": NBASTORAGE.PF" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.PF0: float(fouls)})
                    for i in range(8, -1, -1):
                        exec(
                            "self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update({NBASTORAGE.plusminus" + str(
                                i + 1) + ": NBASTORAGE.plusminus" + str(i) + "})")
                        self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == name).update(
                            {NBASTORAGE.plusminus0: float(pm)})
        return self.sess

    def scrape_league(self):
        """scrape the data about the average in league"""

        # find data in league and team
        print('league_data...')
        league_data = LEAGUE().find_league_statistics()
        # dump into session
        b = self.sess.query(LEAGUE_TABLE)
        # qeury object
        lg_obj = b.filter(LEAGUE_TABLE.lgname == 'league')
        # LEAGUE_TABLE object
        lgtable_obj = lg_obj.first()
        print('update LEAGUE_TABLE...')
        if not lgtable_obj:
            # cannot find this league, create a new object
            tem = LEAGUE_TABLE('league', league_data[0], league_data[1], league_data[2], league_data[3], league_data[4],
                               league_data[5], league_data[6], league_data[7], league_data[8], league_data[9],
                               league_data[10])
            self.sess.add(tem)
        else:
            # find it! and update
            mark = ['fgm_per_g', 'fga_per_g', 'ftm_per_g', 'fta_per_g', 'pts_per_g', 'ast_per_g', 'orb_per_g',
                    'drb_per_g', 'tov_per_g', 'pf_per_g', 'pace']
            for col, i in zip(mark, range(11)):
                exec(
                    "self.sess.query(LEAGUE_TABLE).filter(LEAGUE_TABLE.lgname == 'league').update({LEAGUE_TABLE." + col + ": league_data[" + str(
                        i) + "]})")
        print('\n')
        return self.sess

    def scrape_team(self):
        """scrape the data about the average of each team"""

        print('team_data...')
        # dump into session
        c = self.sess.query(TEAM_TABLE)
        for team in ['ATL', 'BRK', 'BOS', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL',
                     'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR',
                     'UTA', 'WAS']:
            print('find ' + team)
            try:
                team_data, opp_data = TEAM().find_team_statistics(team)
            except:
                print(team, ' cannot be updated')

            ##team
            # qeury object
            tm_obj = c.filter(TEAM_TABLE.teamsname == team)
            # TEAM_TABLE object
            tmtable_obj = tm_obj.first()
            print('update ' + team + ' TEAM_TABLE...')
            if not tmtable_obj:
                # cannot find this team, create a new object
                tem = TEAM_TABLE(team, team_data[0], team_data[1], team_data[2], team_data[3], team_data[4],
                                 team_data[5], team_data[6], team_data[7])
                self.sess.add(tem)
            else:
                # find it! and update
                mark = ['mp_per_g', 'ast_per_g', 'fgm_per_g', 'fga_per_g', 'fta_per_g', 'orb_per_g', 'drb_per_g',
                        'tov_per_g']
                for col, i in zip(mark, range(8)):
                    exec("self.sess.query(TEAM_TABLE).filter(TEAM_TABLE.teamsname == team).update({TEAM_TABLE." + col + ": team_data[" + str(i) + "]})")

            ##opponent
            # qeury object
            opp_obj = c.filter(TEAM_TABLE.teamsname == 'opp' + team)
            # TEAM_TABLE object
            opptable_obj = opp_obj.first()
            print('update opp' + team + ' TEAM_TABLE...')
            if not opptable_obj:
                # cannot find this oppteam, create a new object
                tem = TEAM_TABLE('opp' + team, opp_data[0], opp_data[1], opp_data[2], opp_data[3], opp_data[4],
                                 opp_data[5], opp_data[6], opp_data[7])
                self.sess.add(tem)
            else:
                # find it! and update
                mark = ['mp_per_g', 'ast_per_g', 'fgm_per_g', 'fga_per_g', 'fta_per_g', 'orb_per_g', 'drb_per_g',
                        'tov_per_g']
                for col, i in zip(mark, range(8)):
                    exec("self.sess.query(TEAM_TABLE).filter(TEAM_TABLE.teamsname == 'opp' + team).update({TEAM_TABLE." + col + ": opp_data[" + str(i) + "]})")
            print('\n')
        return self.sess


class ANALYSIS(Base_of):
    
    def __init__(self):
        super().__init__()
        self.total_MP_eachgame = [0]*10
        self.accumulated_aPER0 = 0
    def ana_best(self):
        """Find the best data among all the players"""

        # best data
        print("best~")
        a = self.sess.query(NBASTORAGE).order_by(NBASTORAGE.PTS0.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PTS').first():
            tem = BEST_TABLE(a.playersname, 'PTS', a.PTS0)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PTS').update(
                {BEST_TABLE.bestname: a.playersname, BEST_TABLE.data: a.PTS0})

        a = self.sess.query(NBASTORAGE).order_by(NBASTORAGE.AST0.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'AST').first():
            tem = BEST_TABLE(a.playersname, 'AST', a.AST0)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'AST').update(
                {BEST_TABLE.bestname: a.playersname, BEST_TABLE.data: a.AST0})

        a = self.sess.query(NBASTORAGE).order_by(NBASTORAGE.BLK0.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'BLK').first():
            tem = BEST_TABLE(a.playersname, 'BLK', a.BLK0)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'BLK').update(
                {BEST_TABLE.bestname: a.playersname, BEST_TABLE.data: a.BLK0})

        a = self.sess.query(NBASTORAGE).order_by(NBASTORAGE.TOV0.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'TOV').first():
            tem = BEST_TABLE(a.playersname, 'TOV', a.TOV0)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'TOV').update(
                {BEST_TABLE.bestname: a.playersname, BEST_TABLE.data: a.TOV0})

        a = self.sess.query(NBASTORAGE).order_by(NBASTORAGE.EFF0.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'EFF').first():
            tem = BEST_TABLE(a.playersname, 'EFF', a.EFF0)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'EFF').update(
                {BEST_TABLE.bestname: a.playersname, BEST_TABLE.data: a.EFF0})

        a = self.sess.query(NBASTORAGE).order_by(NBASTORAGE.PER0.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PER').first():
            tem = BEST_TABLE(a.playersname, 'PER', a.PER0)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PER').update(
                {BEST_TABLE.bestname: a.playersname, BEST_TABLE.data: a.PER0})
        return self.sess

    def eff_calculation(self):
        """After scraping, this method can calculate EFF0 for each player."""

        a = self.sess.query(NBASTORAGE).all()
        for player in a:
            # these data are float type~
            eff = player.PTS0 + +player.ORB0 + +player.DRB0 + +player.AST0 + player.STL0 + player.BLK0 - (player.FGA0 - player.FGM0) - (player.FTA0 - player.FTM0) - player.TOV0
            self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == player.playersname).update({NBASTORAGE.EFF0: eff})
            print(player.playersname, 'finish EFF calculation:', player.EFF0)
        return self.sess
    
    def league_parameter_calculation(self):
        """After scraping, this method can calculate some parameters in league, including  factor, VOP and DRBP."""
        ##league constant factor
        # query object
        bb = self.sess.query(LEAGUE_TABLE)
        # LEAGUE_TABLE object
        b = bb.first()
        # to show the feasibility of offense among past and future
        factor = (2 / 3) - (0.5 * (b.ast_per_g / b.fgm_per_g)) / (2 * (b.fgm_per_g / b.ftm_per_g))
        # value of possession, to show the eff of offense among all player(league)
        VOP = b.pts_per_g / (b.fga_per_g - b.orb_per_g + b.tov_per_g + 0.44 * b.fta_per_g)
        # defensive rebound percentage, to show the ability of defense among all player
        DRBP = ((b.drb_per_g + b.orb_per_g) - b.orb_per_g) / (b.drb_per_g + b.orb_per_g)
        # update to session
        self.sess.query(LEAGUE_TABLE).update({LEAGUE_TABLE.factor: factor, LEAGUE_TABLE.VOP: VOP, LEAGUE_TABLE.DRBP: DRBP})
        
        return self.sess
    
    def team_parameter_calculation(self):
        ##team constant factor
        totalteam_list = ['ATL', 'BRK', 'BOS', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC',
                          'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC',
                          'SAS', 'TOR', 'UTA', 'WAS']
        
        cc = self.sess.query(TEAM_TABLE)
        for t in totalteam_list:
            # query. eg: ATL and oppATL
            cc_query = cc.filter(or_(TEAM_TABLE.teamsname == t, TEAM_TABLE.teamsname == 'opp' + t))
            # select one
            t_obj = cc_query.all()[0]
            o_obj = cc_query.all()[1]
            # Possessions(Poss)
            tmPoss = t_obj.fga_per_g + 0.4 * t_obj.fta_per_g - 1.07 * (
                        t_obj.orb_per_g / (t_obj.orb_per_g + o_obj.drb_per_g)) * (
                                 t_obj.fga_per_g - t_obj.fgm_per_g) + t_obj.tov_per_g
            oppPoss = o_obj.fga_per_g + 0.4 * o_obj.fta_per_g - 1.07 * (
                        o_obj.orb_per_g / (o_obj.orb_per_g + t_obj.drb_per_g)) * (
                                  o_obj.fga_per_g - o_obj.fgm_per_g) + o_obj.tov_per_g
            # pace factor
            tmPace = 48 * ((tmPoss + oppPoss) / (2 * (t_obj.mp_per_g / 5)))
            # update to session
            cc_query.filter(TEAM_TABLE.teamsname == t).update(
                {TEAM_TABLE.tmPOSS: tmPoss, TEAM_TABLE.oppPOSS: oppPoss, TEAM_TABLE.tmPACE: tmPace})
            print(t, ' tmPACE is ', cc_query.filter(TEAM_TABLE.teamsname == t).first().tmPACE)
        
        return self.sess
    
    def a_per_calculation(self):
        """After scraping, this method can calculate adjested PER in the latest game for each player."""
        
        # import league data
        lg = self.sess.query(LEAGUE_TABLE).first()
        for player in self.sess.query(NBASTORAGE).all():
            # team object eg: t_obj.ast_per_g
            # player object eg: player.AST
            t_obj = self.sess.query(TEAM_TABLE).filter(TEAM_TABLE.teamsname == player.team).first()
            if not t_obj:
                sys.exit(player.playersname + 'cannot find his team!')

            # unadjusted PER
            if player.ontime0 >= 5:
                r_min = (1 / player.ontime0)
            else:
                r_min = 0

            block1 = player.TPM0
            block2 = (2/3)*player.AST0
            # (tmAST/tmFGM) is that the preference of scoring from others AST or personal offense
            preference_of_scoring = (t_obj.ast_per_g / t_obj.fgm_per_g)
            block3 = (2 - lg.factor*preference_of_scoring)*player.FGM0
            # free throw considering (tmAST/tmFG)
            block4 = (player.FTM0*0.5*(2-(1/3)*preference_of_scoring))
            # turnovers
            block5 = lg.VOP*player.TOV0
            # missing field goal
            block6 = lg.VOP*lg.DRBP*(player.FGA0 - player.FGM0)
            # missing free throw
            block7 = lg.VOP*0.44*(0.44+(0.56*lg.DRBP))*(player.FTA0 - player.FTM0)
            # defense rebounds
            total_RB = player.ORB0 + player.DRB0
            block8 = lg.VOP*(1-lg.DRBP)*(total_RB - player.ORB0)
            # offense rebounds
            block9 = lg.VOP*lg.DRBP*player.ORB0
            # steal
            block10 = lg.VOP*player.STL0
            # block considering defense rebounds
            block11 = lg.VOP*lg.DRBP*player.BLK0
            # fouls considering the effect after foul
            block12 = player.PF0*((lg.ftm_per_g/lg.pf_per_g)-0.44*(lg.fta_per_g/lg.pf_per_g)*lg.VOP)
            uPER = r_min * (block1 + block2 + block3 + block4 - block5 - block6 - block7 + block8 + block9 + block10 + block11 - block12)
            # aPER
            aPER = round(uPER * (lg.pace / t_obj.tmPACE), 2)
            self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == player.playersname).update({NBASTORAGE.aPER0: aPER})
            print('calculate', player.playersname, "'s aPER0: ", aPER)

        return self.sess

    def total_MP_map(self):
        for i in range(10):
            for player in self.sess.query(NBASTORAGE).all():
                exec("self.total_MP_eachgame["+str(i)+"] += player.ontime"+str(i))
        print('total_MP_eachgame0:', self.total_MP_eachgame[0], 'total_MP_eachgame1:', self.total_MP_eachgame[1])

    def per_calculation(self):
        ## calculate lg_aPER(sigma(MPi*aPERi/Min))
        # accumulate aPER
        buffer = []
        a = self.sess.query(NBASTORAGE).all()
        for player in a:
            buffer.append(player.aPER0)
        self.accumulated_aPER0 = np.mean(buffer)

        ## calculate PER
        for player in a:
            if self.accumulated_aPER0 != 0:
                PER = round(player.aPER0*(15/self.accumulated_aPER0),2)
            elif self.accumulated_aPER0 == 0:
                PER = 0
            for i in range(8,-1,-1):
                exec("self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == player.playersname).update({NBASTORAGE.PER"+str(i+1)+": NBASTORAGE.PER"+str(i)+"})")
            exec("self.sess.query(NBASTORAGE).filter(NBASTORAGE.playersname == player.playersname).update({NBASTORAGE.PER0: float(PER)})")
            print(player.playersname,"'s PER0 is: ",PER)
        return self.sess


###############################################################################
###############################################################################
###############################################################################
''' Table '''
conn,session = SCRAPPING().call_session()
###############################################################################
# database obj
Base_players = declarative_base()
Base_teams = declarative_base()
Base_league = declarative_base()
Base_date = declarative_base()
Base_mean = declarative_base()
Base_best = declarative_base()
###############################################################################

class LEAGUE_TABLE(Base_league):
    __tablename__ = 'league_data'
    mark = ['fgm_per_g','fga_per_g','ftm_per_g','fta_per_g','pts_per_g','ast_per_g','orb_per_g','drb_per_g','tov_per_g','pf_per_g','pace','factor','VOP','DRBP']
    lgname = Column('league',String(10),primary_key=True,index=True)
    for col in mark:
        exec(col+"=Column('"+col+"',Float)")

    def __init__(self,lgname,fgm_per_g,fga_per_g,ftm_per_g,fta_per_g,pts_per_g,ast_per_g,orb_per_g,drb_per_g,tov_per_g,pf_per_g,pace):
        self.lgname = 'league'
        for col in self.mark[:11]:
            exec("self."+col+"="+col)
        self.factor = 0.0
        self.VOP = 0.0
        self.DRBP = 0.0

    def __repr__(self):
        repr_str1 = "<LEAGUE_TABLE("
        repr_str2 = "league: {}\n"
        repr_str3 = "FGM: {}\n"
        repr_str4 = "FGA: {}\n"
        repr_str5 = "FTM: {}\n"
        repr_str6 = "FTA: {}\n"
        repr_str7 = "PTS: {}\n"
        repr_str8 = "AST: {}\n"
        repr_str9 = "ORB: {}\n"
        repr_str10 = "DRB: {}\n"
        repr_str11 = "TOV: {}\n"
        repr_str12 = "PF: {}\n"
        repr_str13 = "Pace: {}\n"
        repr_str14 = ")>"
        repr_str = repr_str1+repr_str2+repr_str3+repr_str4+repr_str5+repr_str6+repr_str7+repr_str8+repr_str9+repr_str10+repr_str11+repr_str12+repr_str13+repr_str14
        return repr_str.format(self.lgname,self.fgm_per_g,self.fga_per_g,self.ftm_per_g,self.fta_per_g,self.pts_per_g,self.ast_per_g,self.orb_per_g,self.drb_per_g,self.tov_per_g,self.pf_per_g,self.pace)


class PLAYER_MEAN_TABLE(Base_mean):
    __tablename__ = 'player_mean_data'
    name = Column('name',String(40),primary_key=True,index=True)
    mark = ['ontime','PTS','AST','STL','BLK','FGA','FGM','FTA','FTM','TPA','TPM','ORB','DRB','TOV','PF','plusminus','aPER','PER','EFF']
    for col in mark:
        exec(col+"=Column('"+col+"',Float)")

    def __init__(self,name,ontime,PTS,AST,STL,BLK,FGA,FGM,FTA,FTM,TPA,TPM,ORB,DRB,TOV,PF,plusminus,aPER,PER,EFF):
        self.name = name
        for col in self.mark:
            exec("self."+col+"="+col)

    def __repr__(self):
        repr_str1 = "<PLAYER_MEAN_TABLE(\n"
        repr_str1_5 = "name: {}\n"
        repr_str2 = "ontime: {}\n"
        repr_str3 = "PTS: {}\n"
        repr_str4 = "AST: {}\n"
        repr_str5 = "STL: {}\n"
        repr_str6 = "BLK: {}\n"
        repr_str7 = "FGA: {}\n"
        repr_str8 = "FGM: {}\n"
        repr_str9 = "FTA: {}\n"
        repr_str10 = "FTM: {}\n"
        repr_str11 = "TPA: {}\n"
        repr_str12 = "TPM: {}\n"
        repr_str13 = "ORB: {}\n"
        repr_str14 = "DRB: {}\n"
        repr_str15 = "TOV: {}\n"
        repr_str16 = "PF: {}\n"
        repr_str17 = "pm: {}\n"
        repr_str18 = "aPER: {}\n"
        repr_str19 = "PER: {}\n"
        repr_str20 = "EFF: {}\n"
        repr_str21 = ")>"
        repr_str = repr_str1+repr_str1_5+repr_str2+repr_str3+repr_str4+repr_str5+repr_str6+repr_str7+repr_str8+repr_str9+repr_str10+repr_str11+repr_str12+repr_str13+repr_str14+repr_str15+repr_str16+repr_str17+repr_str18+repr_str19+repr_str20+repr_str21
        return repr_str.format(self.name,self.ontime,self.PTS,self.AST,self.STL,self.BLK,self.FGA,self.FGM,self.FTA,self.FTM,self.TPA,self.TPM,self.ORB,self.DRB,self.TOV,self.PF,self.plusminus,self.aPER,self.PER,self.EFF)


class TEAM_TABLE(Base_teams):
    __tablename__ = 'team_data'
    mark = ['mp_per_g','ast_per_g','fgm_per_g','fga_per_g','fta_per_g','orb_per_g','drb_per_g','tov_per_g','tmPOSS','oppPOSS','tmPACE']
    teamsname = Column('team',String(7),primary_key=True,index=True)
    for col in mark:
        exec(col+"=Column('"+col+"',Float)")

    def __init__(self,teamsname,mp_per_g,ast_per_g,fgm_per_g,fga_per_g,fta_per_g,orb_per_g,drb_per_g,tov_per_g):
        self.teamsname = teamsname
        for col in self.mark[:8]:
            exec("self."+col+"="+col)
        self.tmPOSS = 0.0
        self.oppPOSS = 0.0
        self.tmPACE = 0.0

    def __repr__(self):
        repr_str1 = "<TEAM_TABLE("
        repr_str2 = "team's name: {}\n"
        repr_str3 = "MP: {}\n"
        repr_str4 = "AST: {}\n"
        repr_str5 = "FGM: {}\n"
        repr_str6 = "FGA: {}\n"
        repr_str7 = "FTA: {}\n"
        repr_str8 = "ORB: {}\n"
        repr_str9 = "DRB: {}\n"
        repr_str10 = "TOV: {}\n"
        repr_str11 = ")>"
        repr_str = repr_str1+repr_str2+repr_str3+repr_str4+repr_str5+repr_str6+repr_str7+repr_str8+repr_str9+repr_str10+repr_str11
        return repr_str.format(self.teamsname,self.mp_per_g,self.ast_per_g,self.fgm_per_g,self.fga_per_g,self.fta_per_g,self.orb_per_g,self.drb_per_g,self.tov_per_g)


class BEST_TABLE(Base_best):
    __tablename__ = 'best_data'
    best = Column('best', String(10), primary_key=True, index=True)
    bestname = Column('bestname', String(40),index=True)
    data = Column('data', Float)
    
    def __init__(self,bestname,best,data):
        self.bestname = bestname
        self.best = best
        self.data = data
        
    def __repr__(self):
        return "best_table\nname:{}\nbest:{}\ndata:{}\n".format(self.bestname, self.best,self.data)


class DATE_TABLE(Base_date):
    __tablename__ = 'date_data'
    today = Column('today', String(5), primary_key=True, index=True)
    for i in range(10):
        exec("date"+str(i)+"=Column('data"+str(i)+"',String(5),index=True)")

    def __init__(self,today,date):
        self.today = today
        for i in range(10):
            exec("self.date"+str(i)+"=date["+str(i)+"]")

    def __repr__(self):
        return "<DATE({},{},{},{})>".format(self.today, self.date0, self.date1, self.date2)


class NBASTORAGE(Base_players):
    __tablename__ = 'nba_players_data'
    playersname = Column('name',String(40),index=True,primary_key=True)
    team = Column('team',String(5),index=True)
    #float column (19 columns)
    col_list = ['ontime','PTS','ORB','DRB','AST','STL','BLK','FGA','FGM','FTA','FTM','TPA','TPM','TOV','PF','plusminus','aPER','PER','EFF']
    for col in col_list:
        for i,j in zip(range(10),range(10)):
            exec(col+str(i)+"=Column('"+col+str(i)+"',Float)")
    def __init__(self,playersname,team,ontime,PTS,ORB,DRB,AST,STL,BLK,FGA,FGM,FTA,FTM,TPA,TPM,TOV,PF,plusminus):
        #initiation
        self.playersname = playersname
        self.team = team
        for col in self.col_list[:16]:
            for i,j in zip(range(10),range(10)):
                exec("self."+col+str(i)+"="+col+"["+str(j)+"]")
        for i in range(10):
            exec("self.aPER"+str(i)+"=0.0")
        for i in range(10):
            exec("self.PER"+str(i)+"=0.0")
        for i in range(10):
            exec("self.EFF"+str(i)+"=0.0")
    def __repr__(self):
        dic = {'n':self.playersname,'t':self.team}
        dic_cont1 = {'time0':self.ontime0,'PTS0':self.PTS0,'ORB0':self.ORB0,'DRB0':self.DRB0}
        dic_cont2 = {'AST0':self.AST0,'STL0':self.STL0,'BLK0':self.BLK0,'FGA0':self.FGA0}
        dic_cont3 = {'FGM0':self.FGM0,'FTA0':self.FTA0,'FTM0':self.FTM0,'TPA0':self.TPA0}
        dic_cont4 = {'TPM0':self.TPM0,'TOV0':self.TOV0,'PF0':self.PF0,'plusminus0':self.plusminus0}
        #merge dict
        dic = {**dic,**dic_cont1,**dic_cont2,**dic_cont3,**dic_cont4}
        str_dic = ["<NBASTORAGE(",")"]
        for i in list(dic.keys()):
            if (i != 'n') and (i != 't'):
                str_dic.insert(1,i+":{0["+i+"]},")
        str_dic.insert(1,"team:{0[t]},")
        str_dic.insert(1,"name:{0[n]},")
        #rejoin into a str
        out = " ".join(str_dic)
        return out.format(dic)
    
###############################################################################
# connect engine to database obj
Base_players.metadata.create_all(conn)
Base_teams.metadata.create_all(conn)
Base_league.metadata.create_all(conn)
Base_date.metadata.create_all(conn)
Base_mean.metadata.create_all(conn)
Base_best.metadata.create_all(conn)
###############################################################################
# flushing(update database through conducting the change by SQL commands)
session.commit()
conn.dispose()

