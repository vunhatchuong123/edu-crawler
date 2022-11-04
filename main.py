import os
import re
import time

from dotenv import load_dotenv
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver import FirefoxOptions
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

driver_opts = FirefoxOptions()
driver_opts.add_argument("--incognito")
driver_opts.add_argument("--headless")
driver_opts.add_argument("no-sandbox")
driver_opts.add_argument("--disable-gpu")
driver_opts.add_argument("--disable-dev-shm-usage")
driver_opts.add_argument("no-first-run")

client = MongoClient()

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

href_list = []

HTMLREGEX = re.compile("<.*?>")


def clean_html(raw_html):
    cleantext = re.sub(HTMLREGEX, "", raw_html)
    return cleantext


def infinite_scroll(loading_element_xpath):
    last_height = driver.execute_script("return document.body.scrollHeight")
    match = False
    while match is False:

        print("scroll down")
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)

        try:

            print("Waiting for load bar to disappear")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, loading_element_xpath))
            )
            print("Finished")
            time.sleep(1)

        except TimeoutException:
            print("No more load bar or takes too long to load")
            pass

        new_height = driver.execute_script("return document.body.scrollHeight")
        print("-------------------------------------------------")
        if new_height == last_height:
            match = True

        last_height = new_height
        time.sleep(0.5)


def get_school_list():
    start = time.perf_counter()
    print("******************************************************")
    print("Scroll through the pages to get all school lists")
    infinite_scroll("//*[@id='load-more']")

    schools = driver.find_elements(
        By.XPATH, "//a[@class='mdc-card card-list-item fluid']"
    )
    for school in schools:
        if school not in href_list:
            href_list.append(school.get_attribute("href"))
    print("There are " + str(len(href_list)) + " schools")

    end = time.perf_counter()
    print(end - start)


def find_user_ratings():

    print("******************************************************")
    print("Get comments for each school")

    start = time.perf_counter()

    for href in href_list:
        driver.get(href)

        school_name = driver.find_element(
            By.CSS_SELECTOR, ".content-header__title"
        ).text
        print(school_name)

        last_height = driver.execute_script("return document.body.scrollHeight")
        match = False
        while match is False:

            try:
                if driver.find_element(
                    By.CSS_SELECTOR, "#internal-popup-1144"
                ).is_displayed():
                    driver.find_element(
                        By.CSS_SELECTOR, ".modal-intro > button:nth-child(1)"
                    ).click()

                print("Load more")
                load_more_button = driver.find_element(
                    By.XPATH,
                    "//button[@class='subtle-btn subtle-btn__outlined view-more']",
                )
                if load_more_button.is_enabled or load_more_button.is_displayed:
                    load_more_button.click()
                    time.sleep(1)

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
            except (NoSuchElementException, TimeoutException):
                print("Couldn't click load_more_button")
                break

            new_height = driver.execute_script("return document.body.scrollHeight")

            print("-------------------------------------------------")
            if new_height == last_height:
                match = True
            last_height = new_height
            time.sleep(2)

        ratings = driver.find_elements(By.CLASS_NAME, "comment-block")
        for rates in ratings:
            time.sleep(2)

            print("-------------------------------------------------")
            # count = 0
            user_id = rates.get_attribute("id")
            # while count < 4:
            #     try:
            #         user_id = rates.get_attribute("id")
            #     except StaleElementReferenceException:
            #         print("stale")
            #         count += 1
                # driver.refresh()

            WebDriverWait(driver, 5).until(EC.staleness_of, rates.get_attribute("id"))
            print(user_id)

            comment_post_date = (
                rates.find_element(By.CLASS_NAME, "rating-group")
                .find_element(By.TAG_NAME, "time")
                .text
            )[5:]
            print(comment_post_date)

            comment_block = rates.find_element(By.CLASS_NAME, "comment-block__content")
            comment_title = (
                rates.find_element(By.CLASS_NAME, "comment-block__content")
                .find_element(By.TAG_NAME, "h3")
                .text
            )

            comment = comment_block.find_element(By.CLASS_NAME, "readmore-wrap")
            comment_body = [
                clean_html(x.get_attribute("innerHTML"))
                for i, x in enumerate(comment.find_elements(By.TAG_NAME, "p"))
                if i % 2 == 0
            ]

            read_more_comment = comment.find_elements(By.CLASS_NAME, "readmore-target")
            user_comment = school_name + "\n" + comment_title + "\n" + comment.text

            comment_advice = ""
            for r in read_more_comment:

                try:
                    inner = r.get_attribute("innerHTML")
                except StaleElementReferenceException:
                    print("innerHTML is stale, try refreshing")
                    # driver.refresh()
                    inner = r.get_attribute("innerHTML")
                    pass

                if "strong" in inner:
                    pass
                else:
                    comment_advice = inner

            time.sleep(2)

            user = {
                "_id": user_id,
                "school": school_name,
                "date": comment_post_date,
                "major": comment_body[0],
                "comment": {
                    "title": comment_title,
                    "positive": comment_body[1],
                    "needImprove": comment_body[2],
                    "advice": comment_advice,
                },
            }

            collection.insert_one(user)

        time.sleep(2)

    end = time.perf_counter()
    print(end - start)


def main():
    get_school_list()
    find_user_ratings()


if __name__ == "__main__":

    load_dotenv()

    CONNECTION_STRING = os.getenv("MONGODB_STRING")
    DATABASE = os.getenv("MONGODB_DB")

    db = MongoClient(CONNECTION_STRING).get_database(DATABASE)

    collection = db.get_collection("edu2review")
    main()
