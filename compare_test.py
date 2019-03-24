
from nba_players_class import SCRAPPING,TEAM_TABLE,LEAGUE_TABLE,PLAYER_MEAN_TABLE,BEST_TABLE,DATE_TABLE,Base_of,POOL


ana = Base_of()
conn, session = ana.call_session()

# demo of update function
#ana.update("'Aaron-Gordon'", 'PTS', '3.3')

session.commit()
conn.dispose()