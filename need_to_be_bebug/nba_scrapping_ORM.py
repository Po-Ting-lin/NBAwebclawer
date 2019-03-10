# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:44:22 2019
purpose: scrapping player's data from each game, scrapping league average data
package: SQLalchemy(MYSQL dialect), BeautifulSoup, Selenium
@author: BT
"""
import re
import sys
import time
from sqlalchemy import update
from dbdb.nba_players_class import TEXT,LEAGUE,TEAM,SCRAPPING,NBASTORAGE,TEAM_TABLE,LEAGUE_TABLE


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

###############################################################################
#if someone import this,this code will not be conducted.
if __name__ == '__main__':
    decision1 = 'y'
    #decision1 = input("Scrapping nba players?")
    decision2 = input("Scrapping tmdata and lgdata?")
elif __name__ != '__main__':
    decision1 = 'n'
    decision2 = 'n'    
###############################################################################
#create scrapping object
scrape = SCRAPPING()
#connection and session
conn,session_scrape = scrape.call_session()

if decision1 == 'y':
    #main scrapping
    #nba taiwan website
    url = 'https://tw.global.nba.com/scores/'
    #get main text
    main_text = TEXT(url).get_page_text()
    #get soup
    soup = scrape.call_soup(main_text)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #clean date0 
    session_scrape = scrape.clean_date0()
    #check the date
    session_scrape = scrape.check_date()
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #find each post
    url_list = scrape.find_each_post()
    
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
            a = session_scrape.query(NBASTORAGE)
            #qeury object
            ep = a.filter(NBASTORAGE.playersname == name)
            #NBASTORAGE object
            ep_obj = ep.first()
            if not ep_obj:
                #cannot find this player, create a new object 
                tem = NBASTORAGE(name,team,[ontime]+[0.0]*9,[score]+[0.0]*9,[off_rebounds]+[0.0]*9,[def_rebounds]+[0.0]*9,[assists]+[0.0]*9,[steals]+[0.0]*9,[blocks]+[0.0]*9,[fga]+[0.0]*9,[fgm]+[0.0]*9,[fta]+[0.0]*9,[ftm]+[0.0]*9,[tpa]+[0.0]*9,[tpm]+[0.0]*9,[turnovers]+[0.0]*9,[fouls]+[0.0]*9,[pm]+[0.0]*9)
                session_scrape.add(tem)
                
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
    b = session_scrape.query(LEAGUE_TABLE)
    #qeury object
    lg_obj = b.filter(LEAGUE_TABLE.lgname == 'league')
    #LEAGUE_TABLE object
    lgtable_obj = lg_obj.first()
    print('update LEAGUE_TABLE...')
    if not lgtable_obj:
        #cannot find this league, create a new object
        tem = LEAGUE_TABLE('league',league_data[0],league_data[1],league_data[2],league_data[3],league_data[4],league_data[5],league_data[6],league_data[7],league_data[8],league_data[9],league_data[10])
        session_scrape.add(tem)
    else:
        #find it! and update
        mark = ['fgm_per_g','fga_per_g','ftm_per_g','fta_per_g','pts_per_g','ast_per_g','orb_per_g','drb_per_g','tov_per_g','pf_per_g','pace']
        for col,i in zip(mark,range(11)):
            exec("lg_obj.update({LEAGUE_TABLE."+col+": league_data["+str(i)+"]})")
    print('\n')
    
    print('team_data...')
    #dump into session
    c = session_scrape.query(TEAM_TABLE)
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
            session_scrape.add(tem)
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
            session_scrape.add(tem)
        else:
            #find it! and update
            mark = ['mp_per_g','ast_per_g','fgm_per_g','fga_per_g','fta_per_g','orb_per_g','drb_per_g','tov_per_g']
            for col,i in zip(mark,range(8)):
                exec("opp_obj.update({TEAM_TABLE."+col+": opp_data["+str(i)+"]})")
        print('\n')
###############################################################################
#flushing(update database through conducting the change by SQL commands)
session_scrape.commit()
conn.dispose()