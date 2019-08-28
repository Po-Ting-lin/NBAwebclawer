# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:04:59 2018

## Content

    # Function:
        1. find number

    # Class:
        1. TEXT
        2. LEAGUE
        3. TEAM
        4. Base_of (father of SCRAPPING and ANALYSIS)
        5. SCRAPPING
        6. ANALYSIS

    # Table for Object Relational Mapper (ORM)
        1. LEAGUE_TABLE
        2. PLAYER_PERCENTAGE_TABLE
        3. TEAM_TABLE
        4. BEST_TABLE
        5. DATE_TABLE
        6. POOL

@author: BT
"""
import os
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
        

###############################################################################
class TEXT(object):
    def __init__(self, url):
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
        
    def call_session(self,call_who='Proxy'):
        # read nba player's data, team data, and league data
        # engine = create_engine('mysql+pymysql://<USER>:<PASSWORD>@127.0.0.1/<DATABASE>')

        # read password from .bashrc
        local_mySQL = os.getenv("local_conn")
        cloud_SQL_proxy = os.getenv("proxy_conn")

        # choose one option to connect
        if call_who == 'local':
            # connection in local mySQL
            self.conn = create_engine(local_mySQL, poolclass=NullPool)
        elif call_who == 'Proxy':
            # connection by cloud SQL proxy
            self.conn = create_engine(cloud_SQL_proxy, poolclass=NullPool)
        else:
            self.conn = None

        # set long timeout
        # conn.execute('SET GLOBAL innodb_lock_wait_timeout = 10000;')
        # conn.execute('SET innodb_lock_wait_timeout = 10000;')

        # session:(connection object that communicating ORM with SQL)
        Session = sessionmaker(bind=self.conn, autoflush=False)
        self.sess = Session()
        return self.conn, self.sess


# a child of Base_of
class SCRAPPING(Base_of):
    def __init__(self):
        self.date = '0/0'
        self.year = 0
        self.month = 0
        self.day = 0
        self.soup = None
        self.id_current = -1
        self.debug = [0]
        super().__init__()

    def call_soup(self,main_text):
        """main_text is for the main page"""
        self.soup = BeautifulSoup(main_text, 'html.parser')
        return self.soup

    def check_date(self):
        date = self.soup.find('span', 'day ng-binding').string
        self.year = 2019
        self.month = int(date.split('月')[0].strip(' '))
        self.day = int(date.split('月')[1].split('日')[0].strip(' '))
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
        self.sess = self.check_date()
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # find each post
        url_list = self.find_each_post()

        # update id find the max id in all POOL object
        try:
            self.id_current = self.sess.query(POOL).order_by(POOL.id.desc()).first().id + 1
        except:
            self.id_current = 1
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
                try:
                    ontime_list = find_number(i, 'statTotal.secs">.\w*:.\w*</td>', ontime_list, ontime_bool=True)
                except:
                    break
                # find plusminus
                try:
                    pm_list = find_number(i, '"showPlusMinus">.\w*</td>', pm_list)
                except:
                    break
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
                # sys.exit("len of lists not match!")
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

                # qeury object
                ep = self.sess.query(POOL).filter(POOL.name == name, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day)
                ep_obj = ep.first()
                if not ep_obj:
                    self.debug.append(self.id_current)
                    # cannot find this player, create a new object
                    tem = POOL(self.id_current, name, team, self.year, self.month, self.day, ontime, score, off_rebounds, def_rebounds, assists, steals, blocks, fga, fgm, fta, ftm, tpa,
                    tpm, turnovers, fouls, pm)
                    self.sess.add(tem)
                    # update id
                    self.id_current += 1
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
    def __init__(self, year, month, day):
        super().__init__()
        self.total_MP = dict()
        self.lg_aPER = 0
        self.player_aPER = dict()
        self.year = year
        self.month = month
        self.day = day

        self.id_current = 0
        self.namelist = []
        self.baseline = []
        self.compresstime_data = []

    def ana_best(self):
        """Find the best data today"""

        # best data
        print("best...")
        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).order_by(POOL.PTS.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PTS').first():
            tem = BEST_TABLE(a.name, 'PTS', a.PTS)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PTS').update(
                {BEST_TABLE.bestname: a.name, BEST_TABLE.data: a.PTS})

        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).order_by(POOL.AST.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'AST').first():
            tem = BEST_TABLE(a.name, 'AST', a.AST)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'AST').update(
                {BEST_TABLE.bestname: a.name, BEST_TABLE.data: a.AST})

        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).order_by(POOL.BLK.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'BLK').first():
            tem = BEST_TABLE(a.name, 'BLK', a.BLK)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'BLK').update(
                {BEST_TABLE.bestname: a.name, BEST_TABLE.data: a.BLK})

        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).order_by(POOL.TOV.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'TOV').first():
            tem = BEST_TABLE(a.name, 'TOV', a.TOV)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'TOV').update(
                {BEST_TABLE.bestname: a.name, BEST_TABLE.data: a.TOV})

        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).order_by(POOL.EFF.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'EFF').first():
            tem = BEST_TABLE(a.name, 'EFF', a.EFF)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'EFF').update(
                {BEST_TABLE.bestname: a.name, BEST_TABLE.data: a.EFF})

        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).order_by(POOL.PER.desc()).first()
        if not self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PER').first():
            tem = BEST_TABLE(a.name, 'PER', a.PER)
            self.sess.add(tem)
        else:
            self.sess.query(BEST_TABLE).filter(BEST_TABLE.best == 'PER').update(
                {BEST_TABLE.bestname: a.name, BEST_TABLE.data: a.PER})
        return self.sess

    def eff_calculation(self):
        """After scraping, this method can calculate EFF for each player."""
        # Choose those EFF is equal to zero, even if some of those were already calculated.
        a = self.sess.query(POOL).filter(POOL.EFF == 0.0, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).all()
        for player in a:
            # these data are float type~
            eff = player.PTS + player.ORB + player.DRB + player.AST + player.STL + player.BLK - (player.FGA - player.FGM) - (player.FTA - player.FTM) - player.TOV
            self.sess.query(POOL).filter(POOL.name == player.name, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).update({POOL.EFF: eff})
            print(player.name, 'finish EFF calculation:', player.EFF)
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
        for player in self.sess.query(POOL).filter(POOL.aPER == 0.0, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).all():
            # team object eg: t_obj.ast_per_g
            # player object eg: player.AST
            t_obj = self.sess.query(TEAM_TABLE).filter(TEAM_TABLE.teamsname == player.team).first()
            if not t_obj:
                sys.exit(player.name + 'cannot find his team!')

            # unadjusted PER
            if player.ontime >= 5:
                r_min = (1 / player.ontime)
            else:
                r_min = 0

            block1 = player.TPM
            block2 = (2/3)*player.AST
            # (tmAST/tmFGM) is that the preference of scoring from others AST or personal offense
            preference_of_scoring = (t_obj.ast_per_g / t_obj.fgm_per_g)
            block3 = (2 - lg.factor*preference_of_scoring)*player.FGM
            # free throw considering (tmAST/tmFG)
            block4 = (player.FTM*0.5*(2-(1/3)*preference_of_scoring))
            # turnovers
            block5 = lg.VOP*player.TOV
            # missing field goal
            block6 = lg.VOP*lg.DRBP*(player.FGA - player.FGM)
            # missing free throw
            block7 = lg.VOP*0.44*(0.44+(0.56*lg.DRBP))*(player.FTA - player.FTM)
            # defense rebounds
            total_RB = player.ORB + player.DRB
            block8 = lg.VOP*(1-lg.DRBP)*(total_RB - player.ORB)
            # offense rebounds
            block9 = lg.VOP*lg.DRBP*player.ORB
            # steal
            block10 = lg.VOP*player.STL
            # block considering defense rebounds
            block11 = lg.VOP*lg.DRBP*player.BLK
            # fouls considering the effect after foul
            block12 = player.PF*((lg.ftm_per_g/lg.pf_per_g)-0.44*(lg.fta_per_g/lg.pf_per_g)*lg.VOP)
            uPER = r_min * (block1 + block2 + block3 + block4 - block5 - block6 - block7 + block8 + block9 + block10 + block11 - block12)
            # aPER
            aPER = round(uPER * (lg.pace / t_obj.tmPACE), 2)
            self.sess.query(POOL).filter(POOL.name == player.name, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).update({POOL.aPER: aPER})
            print('calculate', player.name, "'s aPER: ", aPER)

        return self.sess

    def lg_aPER_compute(self, namelist):
        """
        player MP and total MP --> for lg_aPER eg: {"Curry": 120.48, "Lebron": 130.22,...,"all": 1244.23}
        player_aPER --> for lg_aPER
        """
        if namelist:
            buf_total = 0
            for name in namelist:
                buf = 0
                buf_aPER = []
                games = self.sess.query(POOL).filter(POOL.name == name).all()
                print(name, len(games))
                for player in games:
                    buf += player.ontime
                    buf_aPER.append(player.aPER)
                buf_total += buf
                self.total_MP.update({name: buf})
                self.player_aPER.update({name: np.mean(buf_aPER)})
            self.total_MP.update({"all": buf_total})
        else:
            print("namelist == NONE!")
            sys.exit()

        # calculate lg_aPER(sigma(MPi*aPERi/Min))
        for name in namelist:
            self.lg_aPER += self.player_aPER[name] * (self.total_MP[name]/self.total_MP["all"])
        print("lg aPER:", self.lg_aPER)
        return self.lg_aPER

    def per_calculation(self,lg_aper):
        ## calculate PER
        # only calculate Today PER
        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).all()
        for player in a:
            if lg_aper != 0:
                PER = round(player.aPER*(15/lg_aper), 2)
            elif lg_aper == 0:
                PER = 0
            self.sess.query(POOL).filter(POOL.name == player.name, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).update({POOL.PER: float(PER)})
            print(player.name, "'s PER is: ", PER)
        return self.sess

    def find_name(self):
        # name list
        a = self.sess.query(POOL).all()
        for row in a:
            if row.name not in self.namelist:
                self.namelist.append(row.name)
        return self.namelist

    def compresstime_of_each_player(self, time_length=-1, name_list=[]):
        """compress time axis"""

        # name list
        self.namelist = name_list
        count = len(name_list)

        # initialize
        self.compresstime_data = [[0]*18]*len(self.namelist)

        # check current id
        try:
            self.id_current = self.sess.query(PLAYER_PERCENTAGE_TABLE).order_by(PLAYER_PERCENTAGE_TABLE.id.desc()).first().id + 1
        except:
            self.id_current = 1

        # compress
        for i in range(len(self.namelist)):
            # calculate one player at a time


            # determine how many data (a) would like to be compressed
            if time_length == -1:
                a = self.sess.query(POOL).filter(POOL.name == self.namelist[i]).all()
            else:
                a = self.sess.query(POOL).filter(POOL.name == self.namelist[i]).limit(time_length).all()

            # buffer
            data_list = [0]*19

            if self.sess.query(POOL).filter(POOL.name == self.namelist[i]):
                print('Compressing ', str(time_length), ' ', self.namelist[i], self.total_MP[self.namelist[i]], count)

                # averaging
                if self.total_MP[self.namelist[i]] != 0:
                    for different_time_player in a:
                        # Ratio
                        ratio = (different_time_player.ontime / self.total_MP[self.namelist[i]])
                        # Average these data by multiplying the ratio for each game
                        data_list[1] += different_time_player.PTS * ratio
                        data_list[2] += different_time_player.ORB * ratio
                        data_list[3] += different_time_player.DRB * ratio
                        data_list[4] += different_time_player.AST * ratio
                        data_list[5] += different_time_player.STL * ratio
                        data_list[6] += different_time_player.BLK * ratio
                        data_list[7] += different_time_player.FGA * ratio
                        data_list[8] += different_time_player.FGM * ratio
                        data_list[9] += different_time_player.FTA * ratio
                        data_list[10] += different_time_player.FTM * ratio
                        data_list[11] += different_time_player.TPA * ratio
                        data_list[12] += different_time_player.TPM * ratio
                        data_list[13] += different_time_player.TOV * ratio
                        data_list[14] += different_time_player.PF * ratio
                        data_list[15] += different_time_player.plusminus * ratio
                        data_list[16] += different_time_player.aPER * ratio
                        data_list[17] += different_time_player.PER * ratio
                        data_list[18] += different_time_player.EFF * ratio

                        # save the average
                        query_find = self.sess.query(PLAYER_PERCENTAGE_TABLE).filter(PLAYER_PERCENTAGE_TABLE.name == self.namelist[i],
                                                                                     PLAYER_PERCENTAGE_TABLE.timelength == time_length)
                        if query_find.first():
                            query_find.update({PLAYER_PERCENTAGE_TABLE.PTS: round(data_list[1],2),
                                               PLAYER_PERCENTAGE_TABLE.ORB: round(data_list[2],2),
                                               PLAYER_PERCENTAGE_TABLE.DRB: round(data_list[3],2),
                                               PLAYER_PERCENTAGE_TABLE.AST: round(data_list[4],2),
                                               PLAYER_PERCENTAGE_TABLE.STL: round(data_list[5],2),
                                               PLAYER_PERCENTAGE_TABLE.BLK: round(data_list[6],2),
                                               PLAYER_PERCENTAGE_TABLE.FGA: round(data_list[7],2),
                                               PLAYER_PERCENTAGE_TABLE.FGM: round(data_list[8],2),
                                               PLAYER_PERCENTAGE_TABLE.FTA: round(data_list[9],2),
                                               PLAYER_PERCENTAGE_TABLE.FTM: round(data_list[10],2),
                                               PLAYER_PERCENTAGE_TABLE.TPA: round(data_list[11],2),
                                               PLAYER_PERCENTAGE_TABLE.TPM: round(data_list[12],2),
                                               PLAYER_PERCENTAGE_TABLE.TOV: round(data_list[13],2),
                                               PLAYER_PERCENTAGE_TABLE.PF: round(data_list[14],2),
                                               PLAYER_PERCENTAGE_TABLE.plusminus: round(data_list[15],2),
                                               PLAYER_PERCENTAGE_TABLE.aPER: round(data_list[16],2),
                                               PLAYER_PERCENTAGE_TABLE.PER: round(data_list[17],2),
                                               PLAYER_PERCENTAGE_TABLE.EFF: round(data_list[18],2)})
                        else:
                            tem = PLAYER_PERCENTAGE_TABLE(self.id_current, self.namelist[i], time_length, data_list[1],
                                                          data_list[4], data_list[5],
                                                          data_list[6], data_list[7], data_list[8], data_list[9],
                                                          data_list[10], data_list[11], data_list[12], data_list[2],
                                                          data_list[3], data_list[13], data_list[14], data_list[15],
                                                          data_list[16], data_list[17], data_list[18])
                            self.sess.add(tem)
                            self.id_current += 1

                # this player on-time == 0
                else:
                    pass
            count -= 1

        self.compresstime_data[i] = data_list[1:]
        return self.compresstime_data, self.sess
    
    def compress_all_player_all_time(self):
        """compress time and players axis"""

        # Use the data in PLAYER_PERCENTAGE_TABLE
        a = self.sess.query(PLAYER_PERCENTAGE_TABLE).filter(PLAYER_PERCENTAGE_TABLE.timelength == -1).all()
        data_list = [0] * 19
        data_length = len(a)
        for player in a:
            data_list[1] += (player.PTS / data_length)
            data_list[2] += (player.ORB / data_length)
            data_list[3] += (player.DRB / data_length)
            data_list[4] += (player.AST / data_length)
            data_list[5] += (player.STL / data_length)
            data_list[6] += (player.BLK / data_length)
            data_list[7] += (player.FGA / data_length)
            data_list[8] += (player.FGM / data_length)
            data_list[9] += (player.FTA / data_length)
            data_list[10] += (player.FTM / data_length)
            data_list[11] += (player.TPA / data_length)
            data_list[12] += (player.TPM / data_length)
            data_list[13] += (player.TOV / data_length)
            data_list[14] += (player.PF / data_length)
            data_list[15] += (player.plusminus / data_length)
            data_list[16] += (player.aPER / data_length)
            data_list[17] += (player.PER / data_length)
            data_list[18] += (player.EFF / data_length)
        query_find = self.sess.query(PLAYER_PERCENTAGE_TABLE).filter(PLAYER_PERCENTAGE_TABLE.id == 9999)
        if query_find.first():
            query_find.update({PLAYER_PERCENTAGE_TABLE.PTS: round(data_list[1], 2),
                               PLAYER_PERCENTAGE_TABLE.ORB: round(data_list[2], 2),
                               PLAYER_PERCENTAGE_TABLE.DRB: round(data_list[3], 2),
                               PLAYER_PERCENTAGE_TABLE.AST: round(data_list[4], 2),
                               PLAYER_PERCENTAGE_TABLE.STL: round(data_list[5], 2),
                               PLAYER_PERCENTAGE_TABLE.BLK: round(data_list[6], 2),
                               PLAYER_PERCENTAGE_TABLE.FGA: round(data_list[7], 2),
                               PLAYER_PERCENTAGE_TABLE.FGM: round(data_list[8], 2),
                               PLAYER_PERCENTAGE_TABLE.FTA: round(data_list[9], 2),
                               PLAYER_PERCENTAGE_TABLE.FTM: round(data_list[10], 2),
                               PLAYER_PERCENTAGE_TABLE.TPA: round(data_list[11], 2),
                               PLAYER_PERCENTAGE_TABLE.TPM: round(data_list[12], 2),
                               PLAYER_PERCENTAGE_TABLE.TOV: round(data_list[13], 2),
                               PLAYER_PERCENTAGE_TABLE.PF: round(data_list[14], 2),
                               PLAYER_PERCENTAGE_TABLE.plusminus: round(data_list[15], 2),
                               PLAYER_PERCENTAGE_TABLE.aPER: round(data_list[16], 2),
                               PLAYER_PERCENTAGE_TABLE.PER: round(data_list[17], 2),
                               PLAYER_PERCENTAGE_TABLE.EFF: round(data_list[18], 2)})
        else:
            tem = PLAYER_PERCENTAGE_TABLE(9999, 'all', data_length, data_list[1],
                                          data_list[4], data_list[5],
                                          data_list[6], data_list[7], data_list[8], data_list[9],
                                          data_list[10], data_list[11], data_list[12], data_list[2],
                                          data_list[3], data_list[13], data_list[14], data_list[15],
                                          data_list[16], data_list[17], data_list[18])
            self.sess.add(tem)
        return self.sess
###############################################################################
# database connection

conn, session = Base_of().call_session()
# database obj
Base = declarative_base()

###############################################################################


class LEAGUE_TABLE(Base):
    __tablename__ = 'league_data'
    mark = ['fgm_per_g', 'fga_per_g', 'ftm_per_g', 'fta_per_g', 'pts_per_g', 'ast_per_g', 'orb_per_g', 'drb_per_g',
            'tov_per_g', 'pf_per_g', 'pace', 'factor', 'VOP', 'DRBP']
    lgname = Column('league', String(10), primary_key=True, index=True)
    for col in mark:
        exec(col + "=Column('" + col + "',Float)")

    def __init__(self, lgname, fgm_per_g, fga_per_g, ftm_per_g, fta_per_g, pts_per_g, ast_per_g, orb_per_g, drb_per_g,
                 tov_per_g, pf_per_g, pace):
        self.lgname = 'league'
        for col in self.mark[:11]:
            exec("self." + col + "=" + col)
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
        repr_str = repr_str1 + repr_str2 + repr_str3 + repr_str4 + repr_str5 + repr_str6 + repr_str7 + repr_str8 + repr_str9 + repr_str10 + repr_str11 + repr_str12 + repr_str13 + repr_str14
        return repr_str.format(self.lgname, self.fgm_per_g, self.fga_per_g, self.ftm_per_g, self.fta_per_g,
                               self.pts_per_g, self.ast_per_g, self.orb_per_g, self.drb_per_g, self.tov_per_g,
                               self.pf_per_g, self.pace)


class PLAYER_PERCENTAGE_TABLE(Base):
    __tablename__ = 'player percentage'
    id = Column('ID', Integer, primary_key = True)
    name = Column('name', String(40), index=True)
    timelength = Column('time length', Integer)
    mark = ['PTS', 'AST', 'STL', 'BLK', 'FGA', 'FGM', 'FTA', 'FTM', 'TPA', 'TPM', 'ORB', 'DRB', 'TOV', 'PF',
            'plusminus', 'aPER', 'PER', 'EFF']
    for col in mark:
        exec(col + "=Column('" + col + "',Float)")

    def __init__(self, id, name, timelength, PTS, AST, STL, BLK, FGA, FGM, FTA, FTM, TPA, TPM, ORB, DRB, TOV, PF, plusminus,
                 aPER, PER, EFF):
        self.id = id
        self.name = name
        self.timelength = timelength
        for col in self.mark:
            exec("self." + col + "=" + col)

    def __repr__(self):
        repr_str1 = "<PLAYER_MEAN_TABLE(\n"
        repr_str1_5 = "name: {}\n"
        repr_str2 = "timelength: {}\n"
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
        repr_str = repr_str1 + repr_str1_5 + repr_str2 + repr_str3 + repr_str4 + repr_str5 + repr_str6 + repr_str7 + repr_str8 + repr_str9 + repr_str10 + repr_str11 + repr_str12 + repr_str13 + repr_str14 + repr_str15 + repr_str16 + repr_str17 + repr_str18 + repr_str19 + repr_str20 + repr_str21
        return repr_str.format(self.name, self.timelength, self.PTS, self.AST, self.STL, self.BLK, self.FGA, self.FGM,
                               self.FTA, self.FTM, self.TPA, self.TPM, self.ORB, self.DRB, self.TOV, self.PF,
                               self.plusminus, self.aPER, self.PER, self.EFF)


class TEAM_TABLE(Base):
    __tablename__ = 'team_data'
    mark = ['mp_per_g', 'ast_per_g', 'fgm_per_g', 'fga_per_g', 'fta_per_g', 'orb_per_g', 'drb_per_g', 'tov_per_g',
            'tmPOSS', 'oppPOSS', 'tmPACE']
    teamsname = Column('team', String(7), primary_key=True, index=True)
    for col in mark:
        exec(col + "=Column('" + col + "',Float)")

    def __init__(self, teamsname, mp_per_g, ast_per_g, fgm_per_g, fga_per_g, fta_per_g, orb_per_g, drb_per_g,
                 tov_per_g):
        self.teamsname = teamsname
        for col in self.mark[:8]:
            exec("self." + col + "=" + col)
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
        repr_str = repr_str1 + repr_str2 + repr_str3 + repr_str4 + repr_str5 + repr_str6 + repr_str7 + repr_str8 + repr_str9 + repr_str10 + repr_str11
        return repr_str.format(self.teamsname, self.mp_per_g, self.ast_per_g, self.fgm_per_g, self.fga_per_g,
                               self.fta_per_g, self.orb_per_g, self.drb_per_g, self.tov_per_g)


class BEST_TABLE(Base):
    __tablename__ = 'best_data'
    best = Column('best', String(10), primary_key=True, index=True)
    bestname = Column('bestname', String(40), index=True)
    data = Column('data', Float)

    def __init__(self, bestname, best, data):
        self.bestname = bestname
        self.best = best
        self.data = data

    def __repr__(self):
        return "best_table\nname:{}\nbest:{}\ndata:{}\n".format(self.bestname, self.best, self.data)


class DATE_TABLE(Base):
    __tablename__ = 'date_data'
    today = Column('today', String(5), primary_key=True, index=True)
    for i in range(10):
        exec("date" + str(i) + "=Column('data" + str(i) + "',String(5),index=True)")

    def __init__(self, today, date):
        self.today = today
        for i in range(10):
            exec("self.date" + str(i) + "=date[" + str(i) + "]")

    def __repr__(self):
        return "<DATE({},{},{},{})>".format(self.today, self.date0, self.date1, self.date2)


class POOL(Base):
    __tablename__ = 'Nba_players_data'
    id = Column('ID', Integer, primary_key=True)
    name = Column('name', String(40), index=True)
    team = Column('team', String(5), index=True)
    year = Column('Year', Integer)
    month = Column('Month', Integer)
    day = Column('Day', Integer)
    # float column (19 columns)
    col_list = ['ontime', 'PTS', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'FGA', 'FGM', 'FTA', 'FTM', 'TPA', 'TPM', 'TOV',
                'PF', 'plusminus', 'aPER', 'PER', 'EFF']
    for col in col_list:
        exec(col + "= Column('" + col + "',Float)")

    def __init__(self, id, name, team, year, month, day, ontime, PTS, ORB, DRB, AST, STL, BLK, FGA, FGM, FTA, FTM, TPA,
                 TPM, TOV, PF, plusminus):
        self.id = id
        self.name = name
        self.team = team
        self.year = year
        self.month = month
        self.day = day
        for col in self.col_list[:16]:
            exec("self." + col + "=" + col)
        self.aPER = 0.0
        self.PER = 0.0
        self.EFF = 0.0

    def __repr__(self):
        return "POOL:\nname:{}\nteam:{}\nontime:{}\nPTS:{}\nORB:{}\nDRB:{}\nAST:{}\nSTL:{}\nBLK:{}\nFGA:{}\n" \
               "FGM:{}\nFTA:{}\nFTM:{}\nTPA:{}\nTPM:{}\nTOV:{}\nPF:{}\nplusminus:{}".format(self.name, self.team
                                                                                            , self.ontime, self.PTS,
                                                                                            self.ORB, self.DRB,
                                                                                            self.AST, self.STL,
                                                                                            self.BLK, self.FGA, self.FGM
                                                                                            , self.FTA, self.FTM,
                                                                                            self.TPA, self.TPM,
                                                                                            self.TOV, self.PF,
                                                                                            self.plusminus)



###############################################################################
# connect engine to database obj
Base.metadata.create_all(conn)
###############################################################################
# flushing(update database through conducting the change by SQL commands)
session.commit()
conn.dispose()

