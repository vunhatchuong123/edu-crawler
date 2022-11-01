import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

# from selenium.webdriver.chrome.service import Service as ChromiumService
# from webdriver_manager.chrome import ChromeDriverManager


# chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
firefox_driver = webdriver.Firefox(
    service=FirefoxService(GeckoDriverManager().install())
)

driver = firefox_driver
# chrome_driver.get("https://edu2review.com/")
driver.get("https://edu2review.com/")

menu = driver.find_element(
    By.CSS_SELECTOR, "li.desktop-navmenu__list-item:nth-child(5) > a:nth-child(1)"
)
hidden_menu = driver.find_element(
    By.CSS_SELECTOR,
    "li.desktop-navmenu__list-item:nth-child(5) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(3) > a:nth-child(1)",
)


WebDriverWait(driver, 30).until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "li.desktop-navmenu__list-item:nth-child(6) > a:nth-child(1)")
    )
)
actions = ActionChains(driver)
actions.move_to_element(menu)
actions.pause(2)
actions.move_to_element(hidden_menu).click(hidden_menu)
actions.perform()
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".content-header__title"))
)

height = driver.execute_script("return document.body.scrollHeight")
schoo_list = []
hrefs = []
LOADING_ELEMENT_XPATH = "//*[@id='load-more']"

match = False
while match == False:

    # soup = BeautifulSoup(pageHTML.text, "html.parser")
    # school = soup.findAll("small", attrs={"class": "n70"})

    school = driver.find_elements(
        By.XPATH, "//a[@class='mdc-card card-list-item fluid']"
    )
    for sc in school:
        if sc not in hrefs:
            hrefs.append(sc.get_attribute("href"))

        break

    for href in hrefs:
        driver.get(href)
        # rating_block = driver.find_element(By.CSS_SELECTOR, ".comment-group")
        ratings = driver.find_elements(By.CLASS_NAME, "comment-block")
        for rates in ratings:

            # print(rates.get_attribute("innerHTML"))
            print(rates.get_attribute("id"))
            # print(
            #     rates.find_element(
            #         By.CLASS_NAME,
            #         "comment-block__content",
            #     ).text
            # )
            print(
                rates.find_element(By.CLASS_NAME, "readmore-wrap")
                .get_attribute("innerHTML")
            )
            # print(rates.text)

    print("scroll down")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)

    try:

        print("Waiting for load bar to disappear")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, LOADING_ELEMENT_XPATH))
        )
        print("Load bar disappeared")

    except TimeoutException:
        # if timeout exception was raised - it may be safe to
        # assume loading has finished, however this may not
        # always be the case, use with caution, otherwise handle
        # appropriately.
        pass

    match = True
    last_height = driver.execute_script("return document.body.scrollHeight")
    if height == last_height:
        match = True
        print(schoo_list)
        print(len(schoo_list))
        break
    last_height = height

# for href in hrefs:
#     driver.get(href)
#     # rating_block = driver.find_element(By.CSS_SELECTOR, ".comment-group")
#     ratings = driver.find_elements(By.CLASS_NAME, "comment-block")
#     for rates in ratings:
#         print(rates.text)

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
