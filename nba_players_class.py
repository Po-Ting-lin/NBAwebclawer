# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:04:59 2019

@author: BT
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class TEXT(object):
    def __init__(self,url):
        self.url = url
    def get_page_text(self):
        '''A way to get url html text'''
        #set web surfer close
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        chromedriver = r"C:\Users\柏廷\Desktop\python爬蟲\chromedriver.exe"
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


class nbaplayer(object):
    '''Each object represents a NBA player,and their statistic record'''
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
        self.fouls = [0]*10
        
        self.PER = [0]*10
        
    def update_all(self,pm,ontime,score,off_rebounds,def_rebounds,assists,steals,blocks,fgm,fga,tpm,tpa,ftm,fta,turnovers,fouls):
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
        self.fouls.pop(-1)
        self.fouls.insert(0,fouls)
        
    def open_csv_refresh_data(self,list_coming):
        self.team = list_coming[0]
        self.plusminus = list_coming[1:11]
        self.ontime = list_coming[11:21]
        self.score = list_coming[21:31]
        self.off_rebounds = list_coming[31:41]
        self.def_rebounds = list_coming[41:51]
        self.assists = list_coming[51:61]
        self.steals = list_coming[61:71]
        self.blocks = list_coming[71:81]
        self.fgm = list_coming[81:91]
        self.fga = list_coming[91:101]
        self.tpm = list_coming[101:111]
        self.tpa = list_coming[111:121]
        self.ftm = list_coming[121:131]
        self.fta = list_coming[131:141]
        self.turnovers = list_coming[141:151]
        self.fouls = list_coming[151:161]
        
    def update_date(self,date):
        self.plusminus.pop(-1)
        self.plusminus.insert(0,date)
    
    def update_team(self,team):
        self.team = team
        
    def advanced_data(self):
        #FG%
        self.fgp = [round(float(i)/float(j),2) if (float(j) != 0.0) else 0 for i,j in zip(self.fgm,self.fga)]
        #TP%
        self.tpp = [round(float(i)/float(j),2) if (float(j) != 0.0) else 0 for i,j in zip(self.tpm,self.tpa)]
        #FT%
        self.ftp = [round(float(i)/float(j),2) if (float(j) != 0.0) else 0 for i,j in zip(self.ftm,self.fta)]
        #total rebound
        self.trb = [round(float(i)+float(j),2) for i,j in zip(self.off_rebounds,self.def_rebounds)]
        #EFF = (PTS + TRB + AST + STL + BLK) -(FGA-FGM)-(FTA-FTM)-TO
        self.eff = []
        zip_ = zip(self.score,self.trb,self.assists,self.steals,self.blocks,self.fga,self.fgm,self.fta,self.ftm,self.turnovers)
        for i1,i2,i3,i4,i5,i6,i7,i8,i9,i10 in zip_:
            self.eff.append((float(i1)+float(i2)+float(i3)+float(i4)+float(i5))-(float(i6)-float(i7))-(float(i8)-float(i9))-float(i10))
        
    def per(self,team_data,opp_data,league_data):
        '''
        Player_efficiency_rating (PER)
        tmAST: team mean AST
        tmFG: team mean FGM
        lgAST: league mean AST
        lgFG: league mean FGM
        lgFT: league mean FTM
        '''
        #read input
        #league
        if len(league_data) == 12:
            #str to float
            league_data = list(map(float,league_data))
            #read list
            lgFGM,lgFGA,lgFTM,lgFTA,lgPTS,lgAST,lgORB,lgDRB,lgTO,lgPF,lgPace,lgPER = league_data
        else:
            print('league_data is not 12')
        #team
        if len(team_data)+len(opp_data) == 16:
            #str to float
            team_data = list(map(float,team_data))
            opp_data = list(map(float,opp_data))
            #read list
            tmMP,tmAST,tmFGM,tmFGA,tmFTA,tmORB,tmDRB,tmTO = team_data
            oppMP,oppAST,oppFGM,oppFGA,oppFTA,oppORB,oppDRB,oppTO = opp_data
        else:
            print('team_data and opp_data are not 8 respectively')
        
        #to show the feasibility of offense among past and future
        factor = (2/3)-(0.5*(lgAST/lgFGM))/(2*(lgFGM/lgFTM))
        #value of possession, to show the eff of offense among all player(league)
        VOP = lgPTS / (lgFGA - lgORB + lgTO + 0.44*lgFTA)
        #defensive rebound percentage, to show the ability of defense among all player
        DRBP = ((lgDRB+lgORB)-lgORB)/(lgDRB+lgORB)
        #Possessions(Poss)
        tmPoss = 0.96*(tmFGA+tmTO + 0.44*tmFTA-tmORB)
        oppPoss = 0.96*(oppFGA+oppTO + 0.44*oppFTA-oppORB)
        #pace factor
        tmPace = 48*((tmPoss+oppPoss)/(2*(tmMP/5)))
        #str to float
        self.tpm = list(map(float,self.tpm))
        self.assists = list(map(float,self.assists))
        self.fgm = list(map(float,self.fgm))
        self.ftm = list(map(float,self.ftm))
        self.fga = list(map(float,self.fga))
        self.fta = list(map(float,self.fta))
        self.trb = list(map(float,self.trb))
        self.off_rebounds = list(map(float,self.off_rebounds))
        self.steals = list(map(float,self.steals))
        self.blocks = list(map(float,self.blocks))
        self.fouls = list(map(float,self.fouls))
        self.turnovers = list(map(float,self.turnovers))
        
        for game in range(10):
            #unadjusted PER
            try:
                time_int = int(self.ontime[game].split(':')[0]) + round(int(self.ontime[game].split(':')[1])/60,2)
            except:
                time_int = 0
            if time_int >= 5:
                r_min = (1/time_int)
            else:
                r_min = 0
            block1 = self.tpm[game]
            block2 = (2/3)*self.assists[game]
            #(tmAST/tmFG) is that the perference of scoring from otehrs AST or personal offense
            block3 = (2 - factor*(tmAST/tmFGM))*self.fgm[game]
            #free throw considering (tmAST/tmFG)
            block4 = (self.ftm[game]*0.5*(2-(1/3)*(tmAST/tmFGM)))
            #turnovers
            block5 = VOP*self.turnovers[game]
            #missing field goal
            block6 = VOP*DRBP*(self.fga[game]-self.fgm[game])
            #missing free throw
            block7 = VOP*0.44*(0.44+(0.56*DRBP))*(self.fta[game]-self.ftm[game])
            #defense rebounds
            block8 = VOP*(1-DRBP)*(self.trb[game] - self.off_rebounds[game])
            #offense rebounds
            block9 = VOP*DRBP*self.off_rebounds[game]
            #steal
            block10 = VOP*self.steals[game]
            #block considering defense rebounds
            block11 = VOP*DRBP*self.blocks[game]
            #fouls considering the effect after foul
            block12 = self.fouls[game]*((lgFTM/lgPF)-0.44*(lgFTA/lgPF)*VOP)
            uPER = r_min*(block1+block2+block3+block4-block5-block6-block7+block8+block9+block10+block11-block12)
            #aPER
            aPER = uPER*(lgPace/tmPace)
            #PER
            self.PER[game] = round(aPER*(15/lgPER),2)
        
        return self.PER
    

