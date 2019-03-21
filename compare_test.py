
from nba_players_class import SCRAPPING,TEAM_TABLE,LEAGUE_TABLE,NBASTORAGE,PLAYER_MEAN_TABLE,BEST_TABLE,DATE_TABLE



ana = SCRAPPING()
conn, session = ana.call_session()

# demo of update function
#ana.update("'Aaron-Gordon'", 'PTS', '3.3')

session.commit()
conn.dispose()