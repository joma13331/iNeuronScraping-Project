from flask import Flask
from WebApplication import ScraperWebApplication

import pymongo
import urllib

import logging

logging.basicConfig(filename="testLog.log", level=logging.INFO)

try:
    app = Flask(__name__)

    logging.info("Flask app setup completed")

    connect_client = pymongo.MongoClient("mongodb+srv://Jobin_ineuron:" + urllib.parse.quote(
        "Rasengan1@mongodb") + "@clusterineuron.xxvwt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    scrapper_object = ScraperWebApplication(connect_client, "WebScraperProject", "CourseSpecialization", "CourseInfo")
    logging.debug("'ScraperWebApplication' object created successfully")

    app.add_url_rule('/specializations', view_func=scrapper_object.course_specializations, methods=["GET", "POST"])
    app.add_url_rule('/category', view_func=scrapper_object.course_details_for_category, methods=["POST"])

    logging.info("the api for accessing the ineuron courses information completed")
except Exception as e:
    logging.error(str(e))

if __name__ == '__main__':

    try:
        app.run()
        logging.info("Flask App run Successfully")
    except Exception as e:
        logging.error(str(e))
