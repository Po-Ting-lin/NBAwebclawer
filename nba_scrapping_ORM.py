# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:44:22 2019
purpose: scrapping player's data from each game, scrapping league average data
package: SQLalchemy(MYSQL dialect), BeautifulSoup, Selenium
@author: BT
"""

from nba_players_class import TEXT,LEAGUE,TEAM,SCRAPPING,POOL,TEAM_TABLE,LEAGUE_TABLE, find_number

###############################################################################
if __name__ == '__main__':
    decision1 = 'y'
    decision2 = 'n'
    # decision1 = input("Scrapping nba players?")
    # decision2 = input("Scrapping tmdata and lgdata?")
elif __name__ != '__main__':
    decision1 = 'n'
    decision2 = 'n'    
###############################################################################
# create scrapping object
scrape = SCRAPPING()
# connection and session
conn, session_scrape = scrape.call_session()

if decision1 == 'y':
    session_scrape = scrape.scrape_player()

# scrapping team data and league data
if decision2 == 'y':
    session_scrape = scrape.scrape_team()
###############################################################################

# flushing(update database through conducting the change by SQL commands)
session_scrape.commit()
conn.dispose()