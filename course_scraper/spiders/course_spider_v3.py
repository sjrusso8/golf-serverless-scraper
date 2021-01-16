import scrapy
import time
import re
import json
import requests
import os

# from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from .score_card_processor import *

# Getting the file path
CWDIR = get_project_settings().get("BASE_DIR")
scripts = CWDIR / 'course_scraper/spiders/scripts'

class CoursespiderV3Spider(scrapy.Spider):
    name = 'coursespider_v3'
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
                "courseFinderHeader").send_keys("tpc")

            print("Gathering the TPC links")

            time.sleep(4)

            print("Gathering Ohio Links")

            driver.find_element_by_id(
                "courseFinderHeader").send_keys(3 * Keys.BACKSPACE)

        # sleep so the site does its thing
        time.sleep(185)

        # init variable for the html page after the buttons were clicked
        self.html = driver.page_source.encode('utf-8')
        self.sessionid = driver.get_cookie("PHPSESSID")['value']
        self.json_text = driver.find_element_by_id("scrapy-scrapper").text

        driver.close()

    def parse(self, response):
        courses_json = json.loads(self.json_text)

        for course in courses_json:
            gps_url = "/course/gps/" + \
                course['id']+"/"+course['city_url']+'/'+course['name_url']

            yield response.follow(gps_url,
                                  cookies={"PHPSESSID": self.sessionid},
                                  callback=self.parse_gps,
                                  meta={'id_course': course['id'],
                                        'name_url': course['name_url'],
                                        'city_url': course['city_url']})

    def parse_gps(self, response):
        GPS_AJAX_URL = os.getenv("BASE_URL")+'course_mapper/getGPS'
        id_mapper = eval(re.findall("var id_mapper = (.+?);\n",
                                    response.body.decode("utf-8"), re.S)[0])
        id_course = response.request.meta['id_course']
        name_url = response.request.meta['name_url']
        city_url = response.request.meta['city_url']

        score_card_url = os.getenv("BASE_URL")+"course/scorecard/" + \
            id_course+"/"+city_url+'/'+name_url

        gps_response = requests.post(
            GPS_AJAX_URL,
            cookies={"PHPSESSID": self.sessionid},
            data={
                "id_mapper": id_mapper,
                "id_course": id_course
            }).json()

        yield response.follow(score_card_url,
                              cookies={"PHPSESSID": self.sessionid},
                              callback=self.parse_scorecard,
                              meta={"gps_response": gps_response})

    def parse_scorecard(self, response):
        # Gather the meta from the prior responses
        gps_response = response.request.meta['gps_response']
        score_card = create_scorecard(response)

        gps_response['tees'] = score_card

        yield {
            "course_data": gps_response
        }
