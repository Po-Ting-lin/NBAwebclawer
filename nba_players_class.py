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
        #conn = create_engine('mysql+pymysql://root:root@localhost/nba_db',poolclass=NullPool)
        # engine = create_engine('mysql+pymysql://<USER>:<PASSWORD>@127.0.0.1/<DATABASE>')
        conn = create_engine('mysql+pymysql://root:root@127.0.0.1:3309/nba_cloud', poolclass=NullPool)
        # conn.execute('CREATE DEFINER = root@127.0.0.1 FUNCTION fnc_calcWalkedDistance;')
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
    mean = Column('mean',String(7),primary_key=True,index=True)
    mark = ['ontime','PTS','AST','STL','BLK','FGA','FGM','FTA','FTM','TPA','TPM','ORB','DRB','TOV','PF','plusminus','aPER','PER','EFF']
    for col in mark:
        exec(col+"=Column('"+col+"',Float)")
    def __init__(self,ontime,PTS,AST,STL,BLK,FGA,FGM,FTA,FTM,TPA,TPM,ORB,DRB,TOV,PF,plusminus,aPER,PER,EFF):
        self.mean = 'mean'
        for col in self.mark:
            exec("self."+col+"="+col)
    def __repr__(self):
        repr_str1 = "<PLAYER_MEAN_TABLE(\n"
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
        repr_str = repr_str1+repr_str2+repr_str3+repr_str4+repr_str5+repr_str6+repr_str7+repr_str8+repr_str9+repr_str10+repr_str11+repr_str12+repr_str13+repr_str14+repr_str15+repr_str16+repr_str17+repr_str18+repr_str19+repr_str20+repr_str21
        return repr_str.format(self.ontime,self.PTS,self.AST,self.STL,self.BLK,self.FGA,self.FGM,self.FTA,self.FTM,self.TPA,self.TPM,self.ORB,self.DRB,self.TOV,self.PF,self.plusminus,self.aPER,self.PER,self.EFF)

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

###############################################################################
#flushing(update database through conducting the change by SQL commands)
session.commit()
conn.dispose()

