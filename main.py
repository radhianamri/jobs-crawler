from selenium import webdriver

from application import logger
from application.job_page import kalibrr

logger.init()
l = logger.log
l.info("Start running main.py")

driver = webdriver.Chrome('./driver/chromedriver')
curr_page = kalibrr.Kalibrr(driver, 10)