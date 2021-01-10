# Scrapy Crawler for Collection Golf Course Data

This website scraper is used to dynamically scrape a specific website containing data about golf courses.  The data is used in a related project [golf-serverless][1] as part of the backend database.

The scraper dynamically crawls many different websites, and then posts the data to a Django REST API endpoint.

## NOTE! Be nice when scraping

The website and login information have been hidden as to protect the target website from being hit with to many requests.  This github is to show how a scraper was created to parse complex text data into a JSON format and then post that data to an API endpoint.

## Requirements

To run this project you need will need to have Python installed (3.9.0) installed.

To install the requirements on your platform:

    pip install -r requirements.txt

## Getting Started

To start this scraper run this command from the root folder:

    scrapy crawl course_spider_v3


[1]: https://github.com/sjrusso8/golf-api-serverless "golf-serverless"
