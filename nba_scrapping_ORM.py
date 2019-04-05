# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 16:44:22 2018
Purpose: Scrape player's data from each game, Scrape league average data
Package: SQLalchemy (MYSQL dialect), BeautifulSoup, Selenium

@author: BT
"""

from nba_players_class import SCRAPPING

###############################################################################
decision1, decision2 = 'n', 'n'
if __name__ == '__main__':
    decision1 = 'y'
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
    session_scrape = scrape.scrape_league()
###############################################################################

# flushing(update database through conducting the change by SQL commands)
session_scrape.commit()
conn.dispose()