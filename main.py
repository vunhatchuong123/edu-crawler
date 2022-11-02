import csv
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import FirefoxOptions
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
driver_opts = FirefoxOptions()
driver_opts.add_argument("--incognito")
driver_opts.add_argument("headless")

driver_opts.add_argument("no-sandbox")
driver_opts.add_argument("--disable-gpu")
driver_opts.add_argument("--disable-dev-shm-usage")
driver_opts.add_argument("no-first-run")

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

schoo_list = []
href_list = []
user_list = []
comment_list = []
LOADING_ELEMENT_XPATH = "//*[@id='load-more']"


def get_school_list():
    # currentURL = driver.current_url
    last_height = driver.execute_script("return document.body.scrollHeight")
    match = False
    while match is False:
        # lastURL = currentURL

        # print("Last URL: " + lastURL)
        print(last_height)

        print("scroll down")
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)

        try:

            print("Waiting for load bar to disappear")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, LOADING_ELEMENT_XPATH))
            )
            print("Finished")
            time.sleep(1)
            # currentURL = driver.current_url

        except TimeoutException:
            # if timeout exception was raised - it may be safe to
            # assume loading has finished, however this may not
            # always be the case, use with caution, otherwise handle
            # appropriately.
            print("No more load bar or takes too long to load")
            pass

        break

        new_height = driver.execute_script("return document.body.scrollHeight")
        print(new_height)
        print("--------------------------------------------------")
        if new_height == last_height:
            match = True
        last_height = new_height
        time.sleep(2)

    schools = driver.find_elements(
        By.XPATH, "//a[@class='mdc-card card-list-item fluid']"
    )
    for school in schools:
        if school not in href_list:
            href_list.append(school.get_attribute("href"))
    print(len(href_list))


def find_user_ratings():

    for href in href_list:
        driver.get(href)

        last_height = driver.execute_script("return document.body.scrollHeight")
        match = False
        while match is False:

            print(last_height)

            try:
                if driver.find_element(By.XPATH, "//*[@id='internal-popup-1144']"):
                    driver.find_element(By.XPATH, "//*[@id='internal-popup-1144']").click()
                    whandle = driver.window_handles[1]
                    driver.switch_to.window(whandle)
                    driver.close()

            except NoSuchElementException:

                pass

            print("scroll down")

            # Load more
            load_more_button = driver.find_element(
                By.CSS_SELECTOR,
                "#general-review > div.rating-group__grouping-block > div > button",
            )

            load_more_button.click()
            time.sleep(2)
            try:

                print("Waiting to load more comments")
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "#general-review > div.rating-group__grouping-block > div > button",
                        )
                    )
                )
                print("Finishes")

            except TimeoutException:
                # if timeout exception was raised - it may be safe to
                # assume loading has finished, however this may not
                # always be the case, use with caution, otherwise handle
                # appropriately.
                pass

            new_height = driver.execute_script("return document.body.scrollHeight")
            print(new_height)
            print("--------------------------------------------------")
            if new_height == last_height:
                match = True
            last_height = new_height
            time.sleep(2)

        ratings = driver.find_elements(By.CLASS_NAME, "comment-block")
        for rates in ratings:

            # print(rates.get_attribute("innerHTML"))
            print("-------------------------------------------")
            print(rates.get_attribute("id"))
            user_list.append(rates.get_attribute("id"))

            comment_block = rates.find_element(By.CLASS_NAME,
                                               "comment-block__content")
            comments = comment_block.text
            read_more_comment = comment_block.find_elements(
                By.XPATH, "//p[@class='readmore-target']"
            )

            for r in read_more_comment:
                inner = r.get_attribute("innerHTML")
                print(inner)
                read_more_body = ""
                read_more_title = ""

                if "strong" in inner:
                    read_more_title = inner[8:-9]
                else:
                    read_more_body = inner

                comments += read_more_title + read_more_body
                # print(comments)
                comment_list.append(comments)
                time.sleep(1)

        time.sleep(1)
    with open("scraped.txt", mode="w+", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["ID", "COMMENT"])
        for user, comment in zip(user_list, comment_list):
            # print(user + " - " + comment)
            writer.writerow([user, comment])


# while match == False:


#     school = driver.find_elements(
#         By.XPATH, "//a[@class='mdc-card card-list-item fluid']"
#     )
#     for sc in school:
#         if sc not in href_list:
#             href_list.append(sc.get_attribute("href"))

#     for href in href_list:
#         print(href)
#         driver.get(href)

#         # Load more
#         load_more_button = driver.find_element(
#             By.CSS_SELECTOR,
#             "#general-review > div.rating-group__grouping-block > div > button",
#         ).click()
#         try:

#             print("Waiting for load bar to disappear")
#             WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable(
#                     (
#                         By.CSS_SELECTOR,
#                         "#general-review > div.rating-group__grouping-block > div > button",
#                     )
#                 )
#             )
#             print("Load bar disappeared")

#         except TimeoutException:
#             # if timeout exception was raised - it may be safe to
#             # assume loading has finished, however this may not
#             # always be the case, use with caution, otherwise handle
#             # appropriately.
#             pass

#         ratings = driver.find_elements(By.CLASS_NAME, "comment-block")
#         for rates in ratings:

#             # print(rates.get_attribute("innerHTML"))
#             user_list.append(rates.get_attribute("id"))
#             comment_block = rates.find_element(By.CLASS_NAME, "comment-block__content")
#             comments = comment_block.text
#             read_more_comment = comment_block.find_elements(
#                 By.XPATH, "//p[@class='readmore-target']"
#             )

#             for r in read_more_comment:
#                 inner = r.get_attribute("innerHTML")
#                 read_more_body = ""
#                 read_more_title = ""

#                 if "strong" in inner:
#                     read_more_title = inner[8:-9]
#                 else:
#                     read_more_body = inner

#                 comments += read_more_title + read_more_body
#                 comment_list.append(comments)

#     with open("scraped.txt", mode="w+", encoding="utf-8") as f:
#         writer = csv.writer(f, delimiter=";")
#         writer.writerow(["ID", "COMMENT"])
#         for user, comment in zip(user_list, comment_list):
#             # print(user + " - " + comment)
#             writer.writerow([user, comment])
#         continue

#     print("scroll down")
#     driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
#     time.sleep(1)

#     try:

#         print("Waiting for load bar to disappear")
#         WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, LOADING_ELEMENT_XPATH))
#         )
#         print("Load bar disappeared")

#     except TimeoutException:
#         # if timeout exception was raised - it may be safe to
#         # assume loading has finished, however this may not
#         # always be the case, use with caution, otherwise handle
#         # appropriately.
#         pass

#     match = True
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     if height == last_height:
#         match = True
#         print(schoo_list)
#         print(len(schoo_list))
#         break
#     last_height = height

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

get_school_list()
find_user_ratings()
