# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:04:59 2019

@author: BT
"""
import sys
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String,Float,Integer


###############################################################################
class TEXT(object):
    def __init__(self,url):
        self.url = url
    def get_page_text(self):
        '''A way to get url html text'''
        #set web surfer close
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        chromedriver = r"/usr/bin/chromedriver"
        #call automatic control
        try:
            driver =  webdriver.Chrome(chromedriver,chrome_options=chrome_option)
        except:
            print('cannot open webdriver!')
            return 0
        #URL
        driver.get(self.url)
        #get HTML source
        text = driver.page_source
        driver.close()
        return text

class LEAGUE(object): #require class TEXT
    '''purpose: to get lgAST,lgFGM,lgFTM,lgPTS,lgFGA,lgORB,lgDRB,lgTO,lgFTA,lgPF,lgPace,lgPER'''
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
        #Player Efficiency Rating (PER) 2018-2019 League average: 15.0 
        league_data.append('15.0')
        return league_data

class TEAM(object): #require class TEXT
    '''purpose: to get tmMP,tmAST,tmFGM,tmFGA,tmFTA,tmORB,tmDRB,tmTO,oppDRB,oppFGA,oppFGM,oppFTA,oppORB,oppTO'''
    def __init__(self):
        self.team = 'TOR'
    def find_team_statistics(self,team):
        url = "https://www.basketball-reference.com/teams/" + team + "/2019.html"
        main_text = TEXT(url).get_page_text()
        soup = BeautifulSoup(main_text,'html.parser')
        a = soup.find_all("tr")
        team_data = []
        opp_data = []
        mark = ['mp_per_g','ast_per_g','fg_per_g','fga_per_g','fta_per_g','orb_per_g','drb_per_g','tov_per_g']
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

class SCRAPPING(object):
    def __init__(self):
        self.date = '0/0'
        self.sess = None
        self.soup = None
    def call_session(self,call_who='localhost'):
        ##read nba player's data, team data, and league data
        # engine = create_engine('mysql+pymysql://<USER>:<PASSWORD>@127.0.0.1/<DATABASE>')

        #connection in local mySQL
        conn = create_engine('mysql+pymysql://root:root@localhost/nba_db',poolclass=NullPool)

        #connection by cloud SQL proxy
        #conn = create_engine('mysql+pymysql://root:root@127.0.0.1:3309/nba_cloud', poolclass=NullPool)

        #set long timeout
        # conn.execute('SET GLOBAL innodb_lock_wait_timeout = 10000;')
        # conn.execute('SET innodb_lock_wait_timeout = 10000;')
        #session:(connection object that communicating ORM with SQL)
        Session = sessionmaker(bind=conn,autoflush=False)
        self.sess = Session()
        return conn,self.sess
    def call_soup(self,main_text):
        '''main_text is for the main page'''
        self.soup = BeautifulSoup(main_text,'html.parser')
        return self.soup
    def check_date(self):
        date = self.soup.find('span','day ng-binding').string
        date_scrapped = date.split('月')[0].strip(' ') +'/'+ date.split('月')[1].split('日')[0].strip(' ')
        status = True
        try:
            #find record_date
            record_date = self.sess.query(DATE_TABLE).first().date0
        except Exception:
            #no obj in query, create a new one
            print('create a new date obj...')
            record_date = '0/0'
            tem = DATE_TABLE('today',['0/0']*10)
            self.sess.add(tem)
            #stop below code
            status = False
            
        if (record_date != date_scrapped) and (status == True):
            #the obj is exist, but today is not been recorded.
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
            #if this page has already recorded,this code shut down
            sys.exit("this page has already recorded!")
        elif (status == False):
            #create a new object and skip the updating process
            print('skip updating date...')
        return self.sess

    def clean_date0(self):
        aa = self.sess.query(DATE_TABLE)
        aa.update({DATE_TABLE.date0: '0/0'})
        return self.sess
    
    def find_each_post(self):
        post = self.soup.find_all('div',class_="row snapshot-content")
        url_list= []
        for i in post:
            try:
                post_url = str(i.find('a',class_="sib3-game-url stats-boxscore game-status-3")['href'])
                enter = 'https://tw.global.nba.com' + post_url
                if post_url:
                    url_list.append(enter)
            except:
                print('none')
        return url_list

    def mean_of_each_player_analysis(self):
        # scrape = SCRAPPING()
        # conn, session = scrape.call_session()
        player_list = self.sess.query(NBASTORAGE).all()
        playermean = self.sess.query(PLAYER_MEAN_TABLE).filter(PLAYER_MEAN_TABLE.name == 'mean').first()

        # input player to be a list
        # player_list = []
        # for player in aa.all():
        #     if input_player in player.playersname:
        #         player_list.append(player)
        #
        # print('player_list including: ')
        # for i in player_list:
        #     print(i.playersname)

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

            #update PLAYER_MEAN_TABLE
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
            #update session
            # aaa = ['PTS', 'FG%', 'FT%', 'TP%', 'AST', 'STL', 'BLK', 'ORB', 'DRB', 'TOV', 'PER']
            # (name, ontime, PTS, AST, STL, BLK, FGA, FGM, FTA, FTM, TPA, TPM, ORB, DRB, TOV, PF, plusminus, aPER, PER, EFF)
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


###############################################################################
###############################################################################
###############################################################################
''' Table '''
conn,session = SCRAPPING().call_session()
###############################################################################
#database obj
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
    bestname = Column('bestname', String(20),index=True)
    data = Column('data', Float)
    def __init__(self,bestname,best,data):
        self.bestname = bestname
        self.best = best
        self.data = data
    def __repr__(self):
        return "best_table\nname:{}\nbest:{}\ndata:{}\n".format(self.bestname, self.best,self.data)

class DATE_TABLE(Base_date):
    __tablename__ = 'date_data'
    today = Column('today',String(5),primary_key=True,index=True)
    for i in range(10):
        exec("date"+str(i)+"=Column('data"+str(i)+"',String(5),index=True)")
    def __init__(self,today,date):
        self.today = today
        for i in range(10):
            exec("self.date"+str(i)+"=date["+str(i)+"]")
    def __repr__(self):
        return "<DATE({},{},{},{})>".format(self.today,self.date0,self.date1,self.date2)

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
#connect engine to database obj
Base_players.metadata.create_all(conn)
Base_teams.metadata.create_all(conn)
Base_league.metadata.create_all(conn)
Base_date.metadata.create_all(conn)
Base_mean.metadata.create_all(conn)
Base_best.metadata.create_all(conn)
###############################################################################
#flushing(update database through conducting the change by SQL commands)
session.commit()
conn.dispose()

