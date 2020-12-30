# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
import json
import requests
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter


class CourseScraperPipeline:
    # course_editor_url = get_project_settings().get('COURSE_EDITOR_URL')
    course_editor_url = 'http://localhost:8000/api/course_details_editor'

    def process_item(self, item, spider):
        """ Parse the item by poping out the elements 
            and the restructuring it into a dict
        """
        course_data = item.pop("course_data")
        course_info = course_data.pop("course")[0]
        gps_holes = course_data.pop("holes")
        tees = course_data.pop("tees")

        course_info['gps_holes'] = gps_holes
        course_info['tees'] = tees

        res_course = requests.post(
            self.course_editor_url,
            json=course_info
        )

        if res_course.status_code == 201:
            return {
                "Course Code": res_course.status_code,
                "Course URL": res_course.url,
                "Text": "Successfully Created the course and the elements",
            }
        if res_course.status_code != 201:
            return {
                "Course Code": res_course.status_code,
                "Course URL": res_course.url,
                "Failed Text": res_course.text,
            }
        else:
            return {
                "Code": res_course.status_code,
                "URL": res_course.url,
                "Failed Text": res_course.text,
            }
