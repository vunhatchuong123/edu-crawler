# from bs4 import BeautifulSoup
# import requests

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import getpass

import csv

browser = Service('/usr/bin/geckodriver')

# page_to_scrape = requests.get("http://quotes.toscrape.com/")
page_to_scrape = webdriver.Firefox(service=browser)
page_to_scrape.get("http://quotes.toscrape.com/")

page_to_scrape.find_element(By.LINK_TEXT, "Login").click()

WebDriverWait(page_to_scrape, 30).until(
    EC.presence_of_element_located(
        (By.ID,"username")
    )
)
# Input infos
username = page_to_scrape.find_element(By.ID, "username")
password = page_to_scrape.find_element(By.ID, "password")
username.send_keys("admin")
my_pass = getpass.getpass()
password.send_keys()
page_to_scrape.find_element(By.CSS_SELECTOR, "input.btn-primary").click()

quotes = page_to_scrape.find_elements(By.CLASS_NAME, "text")
authors = page_to_scrape.find_elements(By.CLASS_NAME, "author")
# soup = BeautifulSoup(page_to_scrape.text, "html.parser")
# quotes = soup.findAll("small", attrs={"class": "n70"})
# authors = soup.findAll("small", attrs={"class": "author"})

with open("scraped.txt", mode="w+") as f:
    writer = csv.writer(f)
    writer.writerow(["QUOTES","AUTHORS"])
    for quote, author in zip(quotes, authors):
        print(quote.text + " - " + author.text)
        writer.writerow([quote.text, author.text])

