from nba_players_class import NBASTORAGE,SCRAPPING
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


ana = SCRAPPING()
conn, session = ana.call_session()

chrome_option = Options()
chrome_option.add_argument("--headless")
chromedriver = r"/usr/bin/chromedriver"
# call automatic control
try:
    driver = webdriver.Chrome(chromedriver, chrome_options=chrome_option)
except:
    print('cannot open webdriver!')


# URL
url = 'https://www.google.com/search?q=NBA&source=lnms&tbm=isch&sa=X&ved=0ahUKEwidipDm0-LgAhUREqYKHZVnDOUQ_AUIECgD&biw=1920&bih=873'
driver.get(url)
# get HTML source


text = driver.page_source
driver.close()

session.commit()
conn.dispose()