
from nba_players_class import SCRAPPING,TEAM_TABLE,LEAGUE_TABLE,NBASTORAGE,PLAYER_MEAN_TABLE,BEST_TABLE



ana = SCRAPPING()
conn, session = ana.call_session()
session = ana.mean_of_each_player_analysis()

session.commit()
conn.dispose()