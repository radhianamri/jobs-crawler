from typing import Counter
from  ..logger import log
import time

class Kalibrr(object):

    # Constants
    JOB_PAGE = 'Kalibrr'
    MAIN_PAGE_URL = 'https://www.kalibrr.com/job-board/1'
    MAIN_PAGE_TITLE = 'Kalibrr: Where Jobs Find You'

    # Initialize Class and validate content on main page
    def __init__(self, driver, limit=10):
        log.info("Initialize opening {} web page".format(self.__class__))
        self.__limit = limit
        self.__driver = driver
        try:
            driver.get(self.MAIN_PAGE_URL)
            if driver.title != self.MAIN_PAGE_TITLE:
                raiseException("Title of page {} has changed: \'{}\'".format(self.JOB_PAGE, self.__driver.title))
            log.info("Loading page done")
        except Exception as e:
            log.error("Exiting job page {} with error: {}".format(self.JOB_PAGE, e))
            
    def wait_loader(self):
        c = 0

        while(c < self.__limit):
            try:
                _ =  self.__driver.find_element_by_class_name('job-card-body')
                break
            except:
                log.error("page is still loading")
                time.sleep(1)
                c = c+1
        if c == self.__limit:
            raiseException("Unable to open page after {}s".format(self.__limit))

def raiseException(msg):
    log.error(msg)
    raise Exception(msg)
