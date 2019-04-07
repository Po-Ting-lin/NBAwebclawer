from nba_players_class import ANALYSIS,POOL


modify = ANALYSIS(2019,4,7)
conn, session = modify.call_session()

namelist = modify.find_name()
modify.lg_aPER_compute()

session = modify.per_calculation()
session.commit()

# , POOL.year == self.year, POOL.month == self.month, POOL.day == self.day