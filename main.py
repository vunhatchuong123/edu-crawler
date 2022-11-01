from bs4 import BeautifulSoup
import requests

from selenium.webdriver import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromiumService
# from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

import time

# chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
firefox_driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

driver = firefox_driver
# chrome_driver.get("https://edu2review.com/")
driver.get("https://edu2review.com/")

menu =driver.find_element(By.CSS_SELECTOR,"li.desktop-navmenu__list-item:nth-child(5) > a:nth-child(1)")
hiddenmenu = driver.find_element(By.CSS_SELECTOR,"li.desktop-navmenu__list-item:nth-child(5) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(3) > a:nth-child(1)")


WebDriverWait(driver, 30).until( EC.presence_of_element_located( (By.CSS_SELECTOR,"li.desktop-navmenu__list-item:nth-child(6) > a:nth-child(1)")))
actions = ActionChains(driver)
actions.move_to_element(menu)
actions.pause(2)
actions.move_to_element(hiddenmenu).click(hiddenmenu)
actions.perform()
currentURL = driver.current_url

WebDriverWait(driver, 30).until( EC.presence_of_element_located( (By.XPATH,"//small[@class='n70']")))

schoolist = []
match = False
LOADING_ELEMENT_XPATH = "//*[@id='load-more']"
while match == False:
    lastURL = currentURL

    # soup = BeautifulSoup(pageHTML.text, "html.parser")
    # school = soup.findAll("small", attrs={"class": "n70"})

    print("scroll  down")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    schoolname = driver.find_elements(By.XPATH, "//small[@class='n70']")
    print("Get schoolname")
    for sc in schoolname:
        # print(sc.text)
        if sc not in schoolist:
            schoolist.append(sc.text)


    currentURL = driver.current_url

    # driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.XPATH,"//*[@id='load-more']"))



    try:
        # wait for loading element to appear
        # - required to prevent prematurely checking if element
        #   has disappeared, before it has had a chance to appear
        
        # print("Wait for presence of load bar")
        # WebDriverWait(driver, 10
        #     ).until(EC.presence_of_element_located((By.XPATH, LOADING_ELEMENT_XPATH)))
        # print("Load bar spotted")


        # then wait for the element to disappear
        print("Wait for load bar to disappear")
        WebDriverWait(driver, 30
            ).until_not(EC.presence_of_element_located((By.XPATH, LOADING_ELEMENT_XPATH)))
        print("Load bar disappeared")

    except TimeoutException:
        # if timeout exception was raised - it may be safe to 
        # assume loading has finished, however this may not 
        # always be the case, use with caution, otherwise handle
        # appropriately.
        pass 

    # WebDriverWait(driver, 30).until( EC.invisibility_of_element_located((By.CSS_SELECTOR,"#load-more")))

    if currentURL == lastURL:
        match = True
        print(schoolist)
        print(len(schoolist))


# Input infos
# schoolname = page_to_scrape.find_element(By.CLASS_NAME, "n70").click()
# username.send_keys("admin")
# my_pass = getpass.getpass()
# password.send_keys()
# page_to_scrape.find_element(By.CSS_SELECTOR, "input.btn-primary").click()

# quotes = page_to_scrape.find_elements(By.CLASS_NAME, "text")
# authors = page_to_scrape.find_elements(By.CLASS_NAME, "author")

# soup = BeautifulSoup(page_to_scrape.text, "html.parser")
# quotes = soup.findAll("small", attrs={"class": "n70"})
# authors = soup.findAll("small", attrs={"class": "author"})

# with open("scraped.txt", mode="w+") as f:
#     writer = csv.writer(f)
#     writer.writerow(["QUOTES","AUTHORS"])
#     for quote, author in zip(quotes, authors):
#         print(quote.text + " - " + author.text)
#         writer.writerow([quote.text, author.text])

