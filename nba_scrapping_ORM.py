# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:44:22 2019
purpose: scrapping player's data from each game, scrapping league average data
package: SQLalchemy(MYSQL dialect), BeautifulSoup, Selenium
@author: BT
"""
import re
import sys
from bs4 import BeautifulSoup
import time
from sqlalchemy import Column,String,Float,Integer,create_engine,update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from nba_players_class import TEXT,LEAGUE,TEAM

decision1 = input("Scrapping nba players?")
decision2 = input("Scrapping tmdata and lgdata?")


###############################################################################
conn = create_engine('mysql+pymysql://root:Password@123@localhost/nba_testdb',poolclass=NullPool)
#set long timeout
conn.execute('SET GLOBAL innodb_lock_wait_timeout = 10000;')
conn.execute('SET innodb_lock_wait_timeout = 10000;')
###############################################################################
#database obj
Base_players = declarative_base()
Base_teams = declarative_base()
Base_league = declarative_base()
Base_date = declarative_base()
###############################################################################
#session:(connection object that communicating ORM with SQL)
Session = sessionmaker(bind=conn,autoflush=False)
session_players = Session()
session_teams = Session()
session_league = Session()
session_date = Session()
###############################################################################
def find_number(i,target_text,number_list,ontime_bool=False):
    '''Find data_number in text of each player and append it to data_list (target must include "> and <)'''
    target_text_1 = target_text.rpartition('">')[0]+target_text.rpartition('">')[1]
    target_text_2 = target_text.rpartition('<')[1]+target_text.rpartition('<')[2]
    num = re.search(target_text,i).group()
    if (num):
        into = num.rpartition(target_text_1)[2].rpartition(target_text_2)[0]
        if ontime_bool == True:
            into = int(into.split(':')[0]) + round(int(into.split(':')[1])/60,2)
        number_list.append(into)
    else:
        number_list.append('0')
    if ontime_bool == False:
        number_list = list(map(float, number_list))
    return number_list

def find_date(soup):
    ''' input BS4 soup object'''
    #find date
    date = soup.find('span','day ng-binding').string
    date_scrapped = date.split('月')[0].strip(' ') +'/'+ date.split('月')[1].split('日')[0].strip(' ')
    return date_scrapped

def update_attr(ep,attrname,new_value):
    '''query_obj, str, str'''
    temp = []
    for i in range(10):
        exec("temp.append(ep_obj."+attrname+str(i)+")")
    temp.pop(-1)
    if type(new_value) == str:
        new_value = float(new_value)
    temp.insert(0,new_value)
    for i in range(10):
        exec("ep.update({NBASTORAGE."+attrname+str(i)+": temp["+str(i)+"]})")
    return ep


class LEAGUE_TABLE(Base_league):
    __tablename__ = 'league_data'
    mark = ['fgm_per_g','fga_per_g','ftm_per_g','fta_per_g','pts_per_g','ast_per_g','orb_per_g','drb_per_g','tov_per_g','pf_per_g','pace']
    lgname = Column('league',String(10),primary_key=True,index=True)
    for col in mark:
        exec(col+"=Column('"+col+"',Float)")
    def __init__(self,lgname,fgm_per_g,fga_per_g,ftm_per_g,fta_per_g,pts_per_g,ast_per_g,orb_per_g,drb_per_g,tov_per_g,pf_per_g,pace):
        self.lgname = 'league'
        for col in self.mark:
            exec("self."+col+"="+col)
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
    
class TEAM_TABLE(Base_teams):
    __tablename__ = 'team_data'
    mark = ['mp_per_g','ast_per_g','fgm_per_g','fga_per_g','fta_per_g','orb_per_g','drb_per_g','tov_per_g']
    teamsname = Column('team',String(7),primary_key=True,index=True)
    for col in mark:
        exec(col+"=Column('"+col+"',Float)")
    def __init__(self,teamsname,mp_per_g,ast_per_g,fgm_per_g,fga_per_g,fta_per_g,orb_per_g,drb_per_g,tov_per_g):
        self.teamsname = teamsname
        for col in self.mark:
            exec("self."+col+"="+col)
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
    #float column
    col_list = ['ontime','PTS','ORB','DRB','AST','STL','BLK','FGA','FGM','FTA','FTM','TPA','TPM','TOV','PF','plusminus','aPER','PER']
    for col in col_list:
        for i,j in zip(range(10),range(10)):
            exec(col+str(i)+"=Column('"+col+str(i)+"',Float)")
    def __init__(self,playersname,team,ontime,PTS,ORB,DRB,AST,STL,BLK,FGA,FGM,FTA,FTM,TPA,TPM,TOV,PF,plusminus):
        #initiation
        self.playersname = playersname
        self.team = team
        for col in self.col_list[:15]:
            for i,j in zip(range(10),range(10)):
                exec("self."+col+str(i)+"="+col+"["+str(j)+"]")
        for i in range(10):
            exec("self.aPER"+str(i)+"=0.0")
        for i in range(10):
            exec("self.PER"+str(i)+"=0.0")
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

###############################################################################
if decision1 == 'y':
    #main scrapping
    #nba taiwan website
    url = 'https://tw.global.nba.com/scores/'
    main_text = TEXT(url).get_page_text()
    soup = BeautifulSoup(main_text,'html.parser')
    ###############################################################################
    date_scrapped = find_date(soup)
    status = True
    try:
        #find record_date
        record_date = session_date.query(DATE_TABLE).first().date0
    except Exception:
        #no obj in query, create a new one
        print('create a new date obj...')
        tem = DATE_TABLE('today',['2/31']*10)
        session_date.add(tem)
        #stop below code
        status = False
        
    if (record_date != date_scrapped) and (status == True):
        aa = session_date.query(DATE_TABLE)
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
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
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
        fouls_list = []
        pm_list = []
        new_player = []
        print('Start searching the information in \n'+ url_list[k])
        
        #iteratively getting the text
        status = True
        count = 0
        while(status):
            post_maintext = TEXT(url_list[k]).get_page_text()
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
        #get each team from this page
        try:
            team1 = re.search('logos/(.+?)_logo.svg',post_maintext.split('team-img')[1]).group(1)
            team2 = re.search('logos/(.+?)_logo.svg',post_maintext.split('team-img')[2]).group(1)
        except:
            sys.exit("cannot find team from this page!")
        #access the text of this page and define team
        k_number = 0
        status_team = team1
        team_list = []
        for i in player:
            #data cleaning
            if ("showPlusMinus" in i) and(not bool(re.match('" class',i))):
                new_player.append(i)
                team_list.append(status_team)
            else:
                if k_number >= 3:
                    status_team = team2
                k_number += 1
        new_player.pop(0)
        team_list.pop(0)
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
            ontime_list = find_number(i,'statTotal.secs">.\w*:.\w*</td>',ontime_list,ontime_bool=True)
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
            #find fouls
            fouls_list = find_number(i,'.statTotal.fouls">.\w*</td>',fouls_list)
            
           
        #combine name and plusminus
        #check that the name_list are corresponded to the pm_list
        if len(name_list) != (len(ontime_list)+len(pm_list)+len(score_list)+len(off_rebounds_list)+len(def_rebounds_list)+len(assists_list)+len(steals_list)+len(blocks_list)+len(fgm_list)+len(fga_list)+len(tpm_list)+len(tpa_list)+len(ftm_list)+len(fta_list)+len(turnovers_list))/15:
            print('This URL ',url_list[k])
            sys.exit("len of lists not match!")
    
        #update data
        zip_injection = zip(name_list,pm_list,ontime_list,score_list,off_rebounds_list,def_rebounds_list,assists_list,steals_list,blocks_list,fgm_list,fga_list,tpm_list,tpa_list,ftm_list,fta_list,turnovers_list,fouls_list,team_list)
        for name,pm,ontime,score,off_rebounds,def_rebounds,assists,steals,blocks,fgm,fga,tpm,tpa,ftm,fta,turnovers,fouls,team in zip_injection:
            if type(ontime) != float:
                sys.exit("ontime is not float!")
            if (type(name) != str) or (type(team) != str):
                sys.exit("name or team is not string!")
            if (type(score) != float) or (type(off_rebounds) != float):
                sys.exit("score or off_rebounds is not float!")    
            a = session_players.query(NBASTORAGE)
            #qeury object
            ep = a.filter(NBASTORAGE.playersname == name)
            #NBASTORAGE object
            ep_obj = ep.first()
            if not ep_obj:
                #cannot find this player, create a new object 
                tem = NBASTORAGE(name,team,[ontime]+[0.0]*9,[score]+[0.0]*9,[off_rebounds]+[0.0]*9,[def_rebounds]+[0.0]*9,[assists]+[0.0]*9,[steals]+[0.0]*9,[blocks]+[0.0]*9,[fga]+[0.0]*9,[fgm]+[0.0]*9,[fta]+[0.0]*9,[ftm]+[0.0]*9,[tpa]+[0.0]*9,[tpm]+[0.0]*9,[turnovers]+[0.0]*9,[fouls]+[0.0]*9,[pm]+[0.0]*9)
                session_players.add(tem)
                
            else:
                #find it! and update
                ep.update({NBASTORAGE.team: team})
                #update each
                ep = update_attr(ep,'ontime',ontime)
                ep = update_attr(ep,'PTS',score)
                ep = update_attr(ep,'ORB',off_rebounds)
                ep = update_attr(ep,'DRB',def_rebounds)
                ep = update_attr(ep,'AST',assists)
                ep = update_attr(ep,'STL',steals)
                ep = update_attr(ep,'BLK',blocks)
                ep = update_attr(ep,'FGA',fga)
                ep = update_attr(ep,'FGM',fgm)
                ep = update_attr(ep,'FTA',fta)
                ep = update_attr(ep,'FTM',ftm)
                ep = update_attr(ep,'TPA',tpa)
                ep = update_attr(ep,'TPM',tpm)
                ep = update_attr(ep,'TOV',turnovers)
                ep = update_attr(ep,'PF',fouls)
                ep = update_attr(ep,'plusminus',pm)    
###############################################################################
#scrapping team data and league data
if decision2 == 'y':
    #find data in league and team
    print('league_data...')
    league_data = LEAGUE().find_league_statistics()
    #dump into session
    b = session_league.query(LEAGUE_TABLE)
    #qeury object
    lg_obj = b.filter(LEAGUE_TABLE.lgname == 'league')
    #LEAGUE_TABLE object
    lgtable_obj = lg_obj.first()
    print('update LEAGUE_TABLE...')
    if not lgtable_obj:
        #cannot find this league, create a new object
        tem = LEAGUE_TABLE('league',league_data[0],league_data[1],league_data[2],league_data[3],league_data[4],league_data[5],league_data[6],league_data[7],league_data[8],league_data[9],league_data[10])
        session_league.add(tem)
    else:
        #find it! and update
        mark = ['fgm_per_g','fga_per_g','ftm_per_g','fta_per_g','pts_per_g','ast_per_g','orb_per_g','drb_per_g','tov_per_g','pf_per_g','pace']
        for col,i in zip(mark,range(11)):
            exec("lg_obj.update({LEAGUE_TABLE."+col+": league_data["+str(i)+"]})")
    print('\n')
    
    print('team_data...')
    #dump into session
    c = session_teams.query(TEAM_TABLE)
    for team in ['ATL','BRK','BOS','CHO','CHI','CLE','DAL','DEN','DET','GSW','HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL','PHI','PHO','POR','SAC','SAS','TOR','UTA','WAS']:
        print('find '+team)
        try:
            team_data, opp_data = TEAM().find_team_statistics(team)
        except:
            print(team,' cannot be updated')
        
        ##team
        #qeury object
        tm_obj = c.filter(TEAM_TABLE.teamsname == team)
        #TEAM_TABLE object
        tmtable_obj = tm_obj.first()
        print('update '+team+' TEAM_TABLE...')
        if not tmtable_obj:
            #cannot find this team, create a new object
            tem = TEAM_TABLE(team,team_data[0],team_data[1],team_data[2],team_data[3],team_data[4],team_data[5],team_data[6],team_data[7])
            session_teams.add(tem)
        else:
            #find it! and update
            mark = ['mp_per_g','ast_per_g','fgm_per_g','fga_per_g','fta_per_g','orb_per_g','drb_per_g','tov_per_g']
            for col,i in zip(mark,range(8)):
                exec("tm_obj.update({TEAM_TABLE."+col+": team_data["+str(i)+"]})")
                
        ##opponent
        #qeury object
        opp_obj = c.filter(TEAM_TABLE.teamsname == 'opp'+team)
        #TEAM_TABLE object
        opptable_obj = opp_obj.first()
        print('update opp'+team+' TEAM_TABLE...')
        if not opptable_obj:
            #cannot find this oppteam, create a new object
            tem = TEAM_TABLE('opp'+team,opp_data[0],opp_data[1],opp_data[2],opp_data[3],opp_data[4],opp_data[5],opp_data[6],opp_data[7])
            session_teams.add(tem)
        else:
            #find it! and update
            mark = ['mp_per_g','ast_per_g','fgm_per_g','fga_per_g','fta_per_g','orb_per_g','drb_per_g','tov_per_g']
            for col,i in zip(mark,range(8)):
                exec("opp_obj.update({TEAM_TABLE."+col+": opp_data["+str(i)+"]})")
        print('\n')
###############################################################################
#flushing(update database through conducting the change by SQL commands)
session_players.commit()
session_teams.commit()
session_league.commit()
session_date.commit()