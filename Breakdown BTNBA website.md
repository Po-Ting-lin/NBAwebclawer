BTNBA ADDICTS

# Breakdown BTNBA website

## Scrape
---
- ### 從聯合新聞網抓取比賽的球員數據 

https://nba.udn.com/nba/index
![](http://drive.google.com/uc?export=view&id=1dL8lo8e93ZExfhNzER2Wz5Os1Ln8zty3)
圖一：聯合新聞網公告的比賽數據

利用Selenium來開啟自動控制瀏覽器。
```typescript=
    def get_page_text(self):
        """A way to get url html text"""
        # set web surfer close
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        chromedriver = r"/usr/bin/chromedriver"
        # call automatic control
        try:
            driver =  webdriver.Chrome(chromedriver,chrome_options=chrome_option)
        except:
            print('cannot open webdriver!')
            return 0
        # URL
        driver.get(self.url)
        # get HTML source
        text = driver.page_source
        driver.close()
        return text
```
再利用BeautifulSoup分解html找到目標tag，並把各個球員的數據抓下來存至資料庫內。
```typescript=
    def call_soup(self,main_text):
        """main_text is for the main page"""
        self.soup = BeautifulSoup(main_text, 'html.parser')
        return self.soup
        
    def find_each_post(self):
        post = self.soup.find_all('div', class_="row snapshot-content")
        url_list = []
        for i in post:
            try:
                post_url = str(i.find('a', class_="sib3-game-url stats-boxscore game-status-3")['href'])
                enter = 'https://tw.global.nba.com' + post_url
                if post_url:
                    url_list.append(enter)
            except:
                print('none')
        return url_list
    
```


## DataBase
---
- ### 連接mySQL資料庫

使用SQLalchemy連接mySQL資料庫，該資料庫建至在google cloud platform的cloud SQL服務。所以只要有權限，就可以透過任意local端連接該資料庫。
資料庫建構及操作形式為Object Relational Mapper（ORM），將資料表對應到python物件上，這麼做可以簡化複雜的資料庫操作問題。

以下為其中一個ORM的形式寫成的資料表。
```typescript=
class POOL(Base):
    __tablename__ = 'Nba_players_data'
    id = Column('ID', Integer, primary_key=True)
    name = Column('name', String(40), index=True)
    team = Column('team', String(5), index=True)
    year = Column('Year', Integer)
    month = Column('Month', Integer)
    day = Column('Day', Integer)
    # float column (19 columns)
    col_list = ['ontime', 'PTS', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'FGA', 'FGM', 'FTA', 'FTM', 'TPA', 'TPM', 'TOV',
                'PF', 'plusminus', 'aPER', 'PER', 'EFF']
    for col in col_list:
        exec(col + "= Column('" + col + "',Float)")

    def __init__(self, id, name, team, year, month, day, ontime, PTS, ORB, DRB, AST, STL, BLK, FGA, FGM, FTA, FTM, TPA,
                 TPM, TOV, PF, plusminus):
        self.id = id
        self.name = name
        self.team = team
        self.year = year
        self.month = month
        self.day = day
        for col in self.col_list[:16]:
            exec("self." + col + "=" + col)
        self.aPER = 0.0
        self.PER = 0.0
        self.EFF = 0.0

```


## Analysis
---
將存在資料庫的資料抓下來進一步操作。以下為分析的項目：
- Efficiency(EFF)
Efficiency的計算為：
PTS + ORB + DRB + +AST + STL + BLK - (FGA - FGM) - (FTA - FTM) - TOV
```typescript=
    def eff_calculation(self):
        """After scraping, this method can calculate EFF for each player."""
        # Choose those EFF is equal to zero, even if some of those were already calculated.
        a = self.sess.query(POOL).filter(POOL.EFF == 0.0, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).all()
        for player in a:
            # these data are float type~
            eff = player.PTS + +player.ORB + +player.DRB + +player.AST + player.STL + player.BLK - (player.FGA - player.FGM) - (player.FTA - player.FTM) - player.TOV
            self.sess.query(POOL).filter(POOL.name == player.name, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).update({POOL.EFF: eff})
            print(player.name, 'finish EFF calculation:', player.EFF)
        return self.sess
```
計算的複雜度較低，以方便取得該球員簡略的效率指標。
但是太過於簡略，所以有些偏差存在。
- Player efficiency rating (PER)
John Hollinger提出Player efficiency rating，以較嚴僅的方式來評估每一項數據消除各種可能的偏差後，再注入到最終分數內。

1. League parameter calculation: 計算聯盟factor、VOP、DRBP。

2. Team parameter calculation: 計算隊伍和敵對的possesion，再計算成該隊的Pace。

3. aPER calculation: 計算校正每一個隊伍的Pace後的uPER。

```typescript=
    def a_per_calculation(self):
        """After scraping, this method can calculate adjested PER in the latest game for each player."""

        # import league data
        lg = self.sess.query(LEAGUE_TABLE).first()
        for player in self.sess.query(POOL).filter(POOL.aPER == 0.0, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).all():
            # team object eg: t_obj.ast_per_g
            # player object eg: player.AST
            t_obj = self.sess.query(TEAM_TABLE).filter(TEAM_TABLE.teamsname == player.team).first()
            if not t_obj:
                sys.exit(player.name + 'cannot find his team!')

            # unadjusted PER
            if player.ontime >= 5:
                r_min = (1 / player.ontime)
            else:
                r_min = 0

            block1 = player.TPM
            block2 = (2/3)*player.AST
            # (tmAST/tmFGM) is that the preference of scoring from others AST or personal offense
            preference_of_scoring = (t_obj.ast_per_g / t_obj.fgm_per_g)
            block3 = (2 - lg.factor*preference_of_scoring)*player.FGM
            # free throw considering (tmAST/tmFG)
            block4 = (player.FTM*0.5*(2-(1/3)*preference_of_scoring))
            # turnovers
            block5 = lg.VOP*player.TOV
            # missing field goal
            block6 = lg.VOP*lg.DRBP*(player.FGA - player.FGM)
            # missing free throw
            block7 = lg.VOP*0.44*(0.44+(0.56*lg.DRBP))*(player.FTA - player.FTM)
            # defense rebounds
            total_RB = player.ORB + player.DRB
            block8 = lg.VOP*(1-lg.DRBP)*(total_RB - player.ORB)
            # offense rebounds
            block9 = lg.VOP*lg.DRBP*player.ORB
            # steal
            block10 = lg.VOP*player.STL
            # block considering defense rebounds
            block11 = lg.VOP*lg.DRBP*player.BLK
            # fouls considering the effect after foul
            block12 = player.PF*((lg.ftm_per_g/lg.pf_per_g)-0.44*(lg.fta_per_g/lg.pf_per_g)*lg.VOP)
            uPER = r_min * (block1 + block2 + block3 + block4 - block5 - block6 - block7 + block8 + block9 + block10 + block11 - block12)
            # aPER
            aPER = round(uPER * (lg.pace / t_obj.tmPACE), 2)
            self.sess.query(POOL).filter(POOL.name == player.name, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).update({POOL.aPER: aPER})
            print('calculate', player.name, "'s aPER: ", aPER)

        return self.sess
```

4. lg aPER compute: 將全部球員計算出來的aPER以上場時間去平均之，最後得出League aPER。

5. PER calculation: 以League aPER去scaling每個球員的aPER，最後才計算出PER。
```typescript=
    def per_calculation(self,lg_aper):
        ## calculate PER
        # only calculate Today PER
        a = self.sess.query(POOL).filter(POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).all()
        for player in a:
            if lg_aper != 0:
                PER = round(player.aPER*(15/lg_aper), 2)
            elif lg_aper == 0:
                PER = 0
            self.sess.query(POOL).filter(POOL.name == player.name, POOL.year == self.year, POOL.month == self.month, POOL.day == self.day).update({POOL.PER: float(PER)})
            print(player.name, "'s PER is: ", PER)
        return self.sess
```
- 不同球員之間分析
- 同一球員不同歷史分析

## Update Automatically
---
- 排程
linux系統之中，crontab服務可以設計欲執行時間和欲執行的命令。
所以本計畫設計為每天下午兩點開始爬蟲及分析，爬蟲和分析好的資料更新資料庫。
## Web
---
- 網站架設
Django為相似於MVC的MTV架構作為網站框架，model部份負責連結資料庫; template部份為html的網站呈現; view定義函式，提供網站與使用者互動及操作資料庫的功能。

- 網站部屬
架設網站在google cloud platform的app engine服務上。本地不用以任何硬體作為伺服器，同時google cloud platform的監控功能也可以估計計算量及記憶體容量，所以可以當作非常實用的後台監控功能。
