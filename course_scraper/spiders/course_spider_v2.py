import scrapy
import time
import json
import os

from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .score_card_processor import *

# Getting the file path
CWDIR = get_project_settings().get("BASE_DIR")
scripts = CWDIR / 'course_scraper/spiders/scripts'

# Load operating system environment variables and then prepare to use them
GOLF_USERNAME = os.getenv("GOLF_USERNAME")
GOLF_PASSWORD = os.getenv("GOLF_PASSWORD")

class CoursespiderSpider(scrapy.Spider):
    name = 'coursespider_v2'
    allowed_domains = [os.getenv("DOMAIN")]
    start_urls = [os.getenv("STARTING_URL")]

    def __init__(self):
        opts = Options()
        driver_path = os.getenv("SELENIUM_DRIVER")
        opts.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36")
        driver = webdriver.Chrome(
            executable_path=driver_path, options=opts)
        driver.get(os.getenv("STARTING_URL"))

        # Log in
        driver.find_element_by_id("username1").send_keys(os.getenv("GOLF_USERNAME"))
        driver.find_element_by_id("password1").send_keys(os.getenv("GOLF_PASSWORD"))
        driver.find_element_by_id("submit").click()

        # inject script
        with open(scripts / 'intercept_xhr.js', 'r') as xhr_js:
            time.sleep(10)

            script = xhr_js.read()

            driver.execute_script(script)

        with open(scripts / 'click_script.js', 'r') as script_js:
            script = script_js.read()

            driver.execute_script(script)

            driver.find_element_by_id(
                "courseFinderHeader").send_keys("TPC")

            print("Gathering the TPC Links")

            # time.sleep(45)

            # print("Gathering Ohio Links")

            # driver.find_element_by_id(
            #     "courseFinderHeader").send_keys(3 * Keys.BACKSPACE)

        # sleep so the site does its thing
        time.sleep(45)

        # global variable for the html page after the buttons were clicked
        self.html = driver.page_source.encode('utf-8')
        self.sessionid = driver.get_cookie("PHPSESSID")['value']
        self.json_text = driver.find_element_by_id("scrapy-scrapper").text

        driver.close()

    def parse(self, response):
        courses_json = json.loads(self.json_text)

        for course in courses_json:
            course_data = {}
            course_data['id'] = course['id']
            course_data['name'] = course['name']
            course_data['city'] = course['city'].title()
            course_data['state'] = course['state']
            course_data['name_url'] = course['name_url']
            course_data['city_url'] = course['city_url']

            score_card_url = "/course/scorecard/" + \
                course['id']+"/"+course['city_url']+'/'+course['name_url']

            yield response.follow(score_card_url,
                                  cookies={"PHPSESSID": self.sessionid},
                                  callback=self.parse_scorecard,
                                  meta={"course_data": course_data})

    def parse_scorecard(self, response):
        """Parse the Score Card from the site"""
        # Gather the meta from the prior responses
        course_data = response.request.meta['course_data']
        score_card = create_scorecard(response)

        course_data['tees'] = score_card

        yield {
            "course_data": course_data
        }
