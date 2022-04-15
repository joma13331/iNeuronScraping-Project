from flask import request, jsonify
import logging

logging.basicConfig(filename="testLog.log", level=logging.INFO)


class ScraperWebApplication:
    """
    This class has been created to expose a modular API for the course information about all courses available in
    ineuron.ai website which is stored in MongoDB.
    """

    def __init__(self, mongodb_client, database_name, collection_name1, collection_name2):
        """
        This function initializes the class ScraperWebApplication which has methods which create an API using the Flask
         Library.
        :param mongodb_client: The command using which you can connect to the mongoDB where the relevant information is
        hosted
        :param database_name: The name of the database which has the relevant information.
        :param collection_name1: The collection name where the name of category specializations are stored.
        :param collection_name2: The collection name where the complete information about the various courses are stored.
        """
        try:
            self.client = mongodb_client
            self.db = self.client[database_name]
            self.collection1 = self.db[collection_name1]
            self.collection2 = self.db[collection_name2]
            logging.info("Initialization of 'ScraperWebApplication' object completed")
        except Exception as e:
            logging.error(str(e))

    def course_specializations(self):
        """
        This method exposes the details of the specializations available in each category of ineuron courses.
        :return: a jsonified result exposed as an API.
        """
        try:

            special_info = list(self.collection1.find())
            for document in special_info:
                document['_id'] = str(document['_id'])

            logging.info("Information from {} collection in {} database in MongoDB obtained".format(self.collection1,
                                                                                                    self.db))
            return jsonify(special_info)

        except Exception as e:
            logging.error(str(e))
            return jsonify(errors=str(e))

    def course_details_for_category(self):
        """
        This method exposes the complete details of the courses available in each category of ineuron courses based on
        the category passed through the POST method.
        :return: Jsonified version of all details of ech course in a particular category.
        """
        try:
            if request.method == "POST":
                category_type = request.json["Category Type"]
                course_info = list(self.collection2.find({"Category Name": category_type}))

                for document in course_info:
                    document['_id'] = str(document['_id'])

                logging.info(
                    "Information from {} collection in {} database in MongoDB obtained".format(self.collection2,
                                                                                               self.db))
                return jsonify(results=course_info)
        except Exception as e:
            logging.error(str(e))
            return jsonify(errors=str(e))

