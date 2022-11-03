import csv
import time

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

        break
        new_height = driver.execute_script("return document.body.scrollHeight")
        print("--------------------------------------------------")
        if new_height == last_height:
            match = True

        last_height = new_height
        time.sleep(0.5)


def get_school_list():
    start = time.perf_counter()
    infinite_scroll("//*[@id='load-more']")

    schools = driver.find_elements(
        By.XPATH, "//a[@class='mdc-card card-list-item fluid']"
    )
    for school in schools:
        if school not in href_list:
            href_list.append(school.get_attribute("href"))
    # print(len(href_list))

    end = time.perf_counter()
    print(end - start)


def find_user_ratings():

    start = time.perf_counter()
    user_list = []
    comment_list = []

    for href in href_list:
        driver.get(href)
        print("School name")
        school_name = driver.find_element(By.CSS_SELECTOR, ".content-header__title")

        last_height = driver.execute_script("return document.body.scrollHeight")
        match = False
        while match is False:

            try:
                if driver.find_element(
                    By.CSS_SELECTOR, "#internal-popup-1144"
                ).is_displayed():
                    print(driver.find_element(By.CSS_SELECTOR, "#internal-popup-1144"))
                    driver.find_element(
                        By.CSS_SELECTOR, ".modal-intro > button:nth-child(1)"
                    ).click()

                print("Load more")
                # Load more
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
                pass

            new_height = driver.execute_script("return document.body.scrollHeight")

            print("--------------------------------------------------")
            if new_height == last_height:
                match = True
            last_height = new_height
            time.sleep(1)

        ratings = driver.find_elements(By.CLASS_NAME, "comment-block")
        for rates in ratings:
            time.sleep(2)

            print("-------------------------------------------")

            try:
                user_id = rates.get_attribute("id")
            except StaleElementReferenceException:
                print("stale")
                # driver.refresh()
                user_id = rates.get_attribute("id")
                pass
            WebDriverWait(driver, 5).until(EC.staleness_of, rates.get_attribute("id"))
            print(user_id)
            user_list.append(user_id)

            comment_block = rates.find_element(By.CLASS_NAME, "comment-block__content")
            comments = comment_block.text
            print(comments)
            read_more_comment = comment_block.find_elements(
                By.CLASS_NAME, "readmore-target"
            )

            for r in read_more_comment:

                try:
                    inner = r.get_attribute("innerHTML")
                except StaleElementReferenceException:
                    print("innerHTML is stale, try refreshing")
                    # driver.refresh()
                    inner = r.get_attribute("innerHTML")
                    pass

                print("Read More")
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
        with open("scraped.txt", mode="a+", encoding="utf-8") as f:
            print("Writing to file....")
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["School", "ID", "COMMENT"])
            for user, comment in zip(user_list, comment_list):
                # print(user + " - " + comment)
                writer.writerow([school_name, user, comment])

    end = time.perf_counter()
    print(end - start)


def main():
    get_school_list()
    find_user_ratings()


if __name__ == "__main__":
    main()
