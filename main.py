from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from application import logger
from application.job_page import kalibrr

logger.init()
l = logger.log
l.info("Start running main.py")

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=chrome_options, executable_path='./driver/chromedriver')
kalibrr = kalibrr.Kalibrr(driver, 10)
kalibrr.find_jobs()

