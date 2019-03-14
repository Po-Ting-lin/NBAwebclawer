
from nba_players_class import SCRAPPING,TEAM_TABLE,LEAGUE_TABLE,NBASTORAGE,PLAYER_MEAN_TABLE,BEST_TABLE,DATE_TABLE



ana = SCRAPPING()
conn, session = ana.call_session()

session.commit()
conn.dispose()