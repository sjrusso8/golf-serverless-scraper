# Scrapy pipeline to post to a Django Rest Framework API
import os
import requests

class CourseScraperPipeline:
    course_editor_url = os.getenv("COURSE_API_URL")

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
