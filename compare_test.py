
from nba_players_class import SCRAPPING,TEAM_TABLE,LEAGUE_TABLE,PLAYER_PERCENTAGE_TABLE,BEST_TABLE,DATE_TABLE,Base_of,POOL
import os

# os.system("/home/bt/cloud_sql_proxy -instances=brian-db-233409:us-central1:brian-new-sql=tcp:3309 -credential_file=/home/bt/文件/brian-key/brian-db-233409-f10c52ae2ae1.json")

ana = Base_of()
conn, session = ana.call_session()



session.commit()
conn.dispose()