from nba_players_class import ANALYSIS,POOL

date_list = [[2019,3,28],[2019,3,29],[2019,3,30],[2019,4,1],[2019,4,2],[2019,4,3],[2019,4,5],[2019,4,6],[2019,4,7]]

modify = ANALYSIS(2019,4,8)
conn, session = modify.call_session()

namelist = modify.find_name()
lg_aper = modify.lg_aPER_compute(namelist)

for i in range(len(date_list)):
    modify = ANALYSIS(date_list[i][0],date_list[i][1],date_list[i][2])
    conn, session = modify.call_session()

    session = modify.per_calculation(lg_aper)
    session.commit()

# , POOL.year == self.year, POOL.month == self.month, POOL.day == self.day