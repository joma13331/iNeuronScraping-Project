import logging

import pymongo
import urllib

from selenium import webdriver
import time

logging.basicConfig(filename="testLog.log", level=logging.INFO)


class WebScraperMongodb:
    """
    This class is created to provide a modular approach to scrape all the relevant information from ineuron.ai website
    about the various courses available at ineuron.
    """

    def __init__(self, mongodb_client, database_name, collection_name1, collection_name2):
        """
        :param mongodb_client: The command using which you can connect to the mongoDB where the relevant information is
        to be stored.
        :param database_name: The name of the database where all the relevant information is to be stored.
        :param collection_name1: The name of the collection where all the relevant information about specializations
        within carious categories is to stored
        :param collection_name2: The name of the collection where all the relevant information about all the courses
        present in the ineuron.ai website
        """
        try:
            self.client = mongodb_client
            self.db = self.client[database_name]
            self.collection1 = self.db[collection_name1]
            self.collection2 = self.db[collection_name2]
            logging.info("initialization of WebScraperMongodb successful")

        except Exception as e:
            logging.error(str(e))

    def scroll_bottom(self, webdriver):
        """
        This method is used to scroll the webpage which is being accessed thought the Chrome Webdriver.
        :param webdriver: The Chrome Driver which is controlling the Chrome Application to perform some task

        """
        try:
            SCROLL_PAUSE_TIME = 0.5

            # Get scroll height
            last_height = webdriver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = webdriver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            logging.info("Scrolling to the bottom Successful")
        except Exception as e:
            logging.error("Scrolling to the bottom Unsuccessful")

    def parse_ineuron_course_page(self, category_name, special_name, webdriver_path, url):
        """
        This method parses all the relevant information present in any course page in ineuron Website and stores that
        information into MongoDB which was initialized when the class object was created.
        :param category_name: This is the category to which the course belongs to.
        :param special_name: This is the specialization to which the course belongs to.
        :param webdriver_path: The path where the Chrome Webdriver is available.
        :param url: URL of the course which is to be parsed.

        """
        try:

            course_dict = {}

            course_dict["Category Name"] = category_name
            course_dict["Specialization Name"] = special_name

            # Creating a Chrome Webdriver object
            driver = webdriver.Chrome(executable_path=webdriver_path)
            # Maximising the Chrome Window
            driver.maximize_window()

            # Going to the relevant URL
            driver.get(url)
            # Adding Some time so that Want Consultation pop up can open up
            time.sleep(8)

            # Closing the Want Consultation pop up
            driver.find_element_by_class_name("Modal_modal-content-header__32vjL").find_element_by_tag_name("i").click()

            # Scroll to bottom of the page so that all the information can load
            self.scroll_bottom(driver)

            # PARSING STARTS
            # Code to obtain the course name
            course_dict["Course Name"] = driver.find_element_by_class_name("Hero_course-title__1a-Hg").text

            # Code to obtain the course description
            course_dict["Course Desc"] = driver.find_element_by_class_name("Hero_course-desc__26_LL").text

            # Using try and except here as cases are present where courses are free and in such cases the html code is
            # different and causes an error.
            try:
                # Code to obtain the course price
                course_dict["Course Price"] = driver.find_element_by_class_name(
                    "CoursePrice_dis-price__3xw3G").find_element_by_xpath(".//span").text
            except Exception:
                course_dict["Course Price"] = driver.find_element_by_class_name("CoursePrice_dis-price__3xw3G").text

            # Using try and except here as cases are present where courses Features are absent
            try:
                # Code to obtain the Course_features
                course_dict["Course Features"] = driver.find_element_by_class_name(
                    "CoursePrice_course-features__2qcJp").find_element_by_xpath(".//ul").text.split("\n")
            except Exception as e:
                course_dict["Course Features"] = "None"

            # Using try and except here as cases are present where courses Course Learning are absent
            try:
                # code to obtain What you'll learn
                course_dict["Course Learning"] = driver.find_element_by_class_name(
                    "CourseMeta_content__v6Hf8").find_element_by_xpath(".//ul").text.split("\n")
            except Exception as e:
                course_dict["Course Learning"] = "None"

            # Using try and except here as cases are present where courses Course Requirements are absent
            try:
                # code to obtain Requirements
                course_dict["Course Requirements"] = \
                driver.find_element_by_class_name("CourseMeta_content__v6Hf8").find_elements_by_tag_name("ul")[
                    1].text.split("\n")
            except Exception as e:
                course_dict["Course Requirements"] = "None"

            # Using try and except here as cases are present where View More Button is Absent for Course Curriculum
            try:
                # Click on View More to view all topic Categories
                driver.find_element_by_class_name(
                    "CurriculumAndProjects_view-more-btn__3ggZL").find_element_by_tag_name("i").click()

                # code to obtain course topics and subtopics
                number_topic = len(
                    driver.find_elements_by_class_name("CurriculumAndProjects_curriculum-accordion__2pppc"))
                course_dict["Course Content"] = []
                # print(number_topic)

                for i in range(0, number_topic):
                    # print(i)
                    topic_dict = {}
                    topic_dict["Course Topic"] = \
                    driver.find_elements_by_class_name("CurriculumAndProjects_curriculum-accordion__2pppc")[
                        i].find_element_by_tag_name("span").text
                    topic_dict["Course Subtopic"] = \
                    driver.find_element_by_class_name("CourseMeta_content__v6Hf8").find_elements_by_tag_name("ul")[
                        i + 2].text.split("\n")

                    course_dict["Course Content"].append(topic_dict)

                    if i != number_topic - 1:
                        driver.find_elements_by_class_name("CurriculumAndProjects_curriculum-accordion__2pppc")[
                            i + 1].find_element_by_tag_name("i").click()
                        # time.sleep(.5)

            except Exception as e:
                print(e)
                number_topic = len(driver.find_elements_by_class_name("CurriculumAndProjects_accordion-header__3ALRY"))
                course_dict["Course Content"] = []

                for i in range(0, number_topic):
                    topic_dict = {}
                    topic_dict["Course Topic"] = \
                    driver.find_elements_by_class_name("CurriculumAndProjects_accordion-header__3ALRY")[
                        i].find_element_by_tag_name("span").text.split("\n")
                    topic_dict["Course Subtopic"] = \
                    driver.find_elements_by_class_name("CurriculumAndProjects_accordion-body__3R51L")[
                        i].find_element_by_tag_name("ul").text.split("\n")

                    course_dict["Course Content"].append(topic_dict)

            # Course Mentor Details

            # No of Mentors
            num_mentors = len(driver.find_elements_by_class_name("InstructorDetails_mentor__2hmG8"))
            course_dict["Mentor Details"] = []

            for i in range(num_mentors):
                mentor_info = {}
                mentor_info["Mentor Name"] = driver.find_elements_by_class_name("InstructorDetails_mentor__2hmG8")[
                    i].find_element_by_tag_name("h5").text
                mentor_info["Mentor Description"] = \
                driver.find_elements_by_class_name("InstructorDetails_mentor__2hmG8")[
                    i].find_element_by_tag_name("p").text

                course_dict["Mentor Details"].append(mentor_info)

            self.collection2.insert_one(course_dict)
            logging.info("Course Page at {} successfully parsed for relevant information".format(url))
        except Exception as e:
            logging.error("Parsing of Course Page at {} unsuccessful: {}".format(url, str(e)))

    def get_course_details(self, webdriver_path, category_name, special_name, special_url):
        """
        This method takes in the url where the specialization offered by ineuron us hosted.
        is parses out all the URL links of the courses in that specialization then call the
        "parse_ineuron_course_page" method passing the all the relevant details.

        :param webdriver_path: The path where the Chrome Webdriver is available.
        :param category_name: This is the category to which the course belongs to.
        :param special_name: This is the specialization to which the course belongs to.
        :param special_url: The URL of the Specialization of courses offered by ineuorn

        """
        try:

            # Obtain an Instance of Chrome Driver
            driver = webdriver.Chrome(executable_path=webdriver_path)

            # Open the Specialization_link
            driver.get(special_url)
            self.scroll_bottom(driver)

            num_courses = len(
                driver.find_elements_by_class_name(
                    "Course_right-area__1XUfi"))  # Courses are repeated twice: Divide by 2

            for i in range(int(num_courses / 2)):
                course_link = driver.find_elements_by_class_name("Course_right-area__1XUfi")[
                    i].find_element_by_tag_name("a").get_attribute("href")
                self.parse_ineuron_course_page(category_name, special_name, webdriver_path, course_link)

            logging.info("Specialization page at {} successfully parsed".format(special_url))

        except Exception as e:
            logging.error("Parsing of specialization Page at {} unsuccessful: {}".format(special_url, str(e)))

    def get_specializations(self, driver_path, url):
        """
        This method parses the base ineuron.ai website and obtains the name and URL links of all the specializations
        available in each category as mentioned on the webpage. it also stores the category and specialization names
        into a collection in MongoDB.

        :param driver_path: The path where the Chrome Webdriver is available.
        :param url: Base URL od ineuron.ai

        """
        try:

            # Setting up the Chrome
            DRIVER_PATH = driver_path
            driver = webdriver.Chrome(executable_path=DRIVER_PATH)

            # Opening the ineuron Webpage
            driver.get(url)
            time.sleep(8)

            # closing the "Want a free consultation" pop up
            driver.find_element_by_xpath("//div/i").click()
            time.sleep(1)

            # Click the menu button
            driver.find_element_by_class_name('hamburger').click()
            time.sleep(1)

            # accessing the sidebar content for Category
            side_bar1 = driver.find_element_by_class_name("sidebar-content")

            # Click on courses
            side_bar1.find_element_by_xpath(".//i").click()
            time.sleep(1)

            # Accessing the category sidebar
            side_bar2 = driver.find_elements_by_class_name("sidebar-content")[1]

            # calculate the number of categories
            num_categories = len(side_bar2.find_elements_by_xpath(".//i"))

            for i in range(num_categories):

                # Accessing the category sidebar
                side_bar2 = driver.find_elements_by_class_name("sidebar-content")[1]

                # obtaining catefory name
                category_name = side_bar2.find_elements_by_xpath(".//li")[i].text

                # CLicking one of the category
                side_bar2.find_elements_by_xpath(".//i")[i].click()
                time.sleep(1)

                # Accessing the specification sidebar
                side_bar3 = driver.find_elements_by_class_name("sidebar-content")[2]

                # Calulating the no. of speciallizations
                num_courses = len(side_bar3.find_elements_by_xpath(".//a"))

                for j in range(num_courses):
                    row = {}

                    row["Category Name"] = category_name

                    # Accessing the specification sidebar
                    side_bar3 = driver.find_elements_by_class_name("sidebar-content")[2]

                    # Obtaining the course link
                    row["Specialization Link"] = side_bar3.find_elements_by_xpath(".//a")[j].get_attribute("href")

                    # Obtaining the Course Name
                    row["Specialization Name"] = side_bar3.find_elements_by_xpath(".//li")[j].text

                    # Inserting the specialization details into collection
                    self.collection1.insert_one(row)

                    # Calling the get_course_details function
                    self.get_course_details(driver_path, row["Category Name"], row["Specialization Name"],
                                            row["Specialization Link"])

                # Accessing the specification sidebar header
                side_bar_header3 = driver.find_elements_by_class_name("sidebar-header")[2]

                # clicking on go back button
                side_bar_header3.find_element_by_xpath(".//i").click()
                time.sleep(1)

            self.client.close()

            logging.info("Base Url successfully parsed")
        except Exception as e:
            logging.error("Parsing Unsuccessful for Base Url:{}".format(str(e)))


try:
    connection_client = # Enter the mongodb Client Statement
    logging.debug("MongoDB client Connection successful")

    # Creating the WebScraperMongodb object
    web_scraper_obj = WebScraperMongodb(connection_client, "WebScraperProject", "CourseSpecialization", "CourseInfo")
    logging.debug("WebScraperMongodb object created")

    # Calling the get_specializations method
    web_scraper_obj.get_specializations(
        r'D:\Technical Education\ineuron\python\programming\sudhanshu sirs assignment\iNeuronScraping\chromedriver.exe',
        "https://ineuron.ai/")

    logging.info("Web Scraping Successful")

except Exception as e:
    logging.error("Web Scraping Unsuccessful: {}".format(str(e)))
