from ..logger import log
import time
from datetime import datetime, timedelta
from slugify import slugify
from ..hash import *
import ujson


class Kalibrr(object):
    # Constants
    JOB_PAGE = 'Kalibrr'
    MAIN_PAGE_URL = 'https://www.kalibrr.com/job-board/1?sort=Freshness#job-board-grid'
    MAIN_PAGE_TITLE = 'Kalibrr: Where Jobs Find You'

    XPATH = {
        'job_title': "//div[@class=\'job-post-section job-post-section-summary\']/div/div/h1[@class='job-post-title']",
        'company_name': "//div[@class=\'job-post-section job-post-section-summary\']/div/div/h2[@class='job-post-company-name']",
        'job_location': "//div[@class=\'job-post-section job-post-section-summary\']/div/div/ul[@class='job-post-quick-details']/li[1]/span",
        'salary': "//div[@class=\'job-post-section job-post-section-summary\']/div/div/ul[@class='job-post-quick-details']/li[2]",
        'job_desc_title': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[3]/div[1]/div/div[1]/h2[{0}]",
        'job_desc_details': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[3]/div[1]/div/div[1]/div[{0}]",
        'req_skills_title': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[3]/div[1]/div/div[1]/div[{0}]/h2",
        'req_skills_details': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[3]/div[1]/div/div[1]/div[{0}]/div",
        'job_type': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/ul/li[3]/a",
        'job_post_time': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div/div/div[1]",
        'job_category': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[3]/div[1]/div/div[1]/h2[{0}]/following::div/div/dl[2]/dd/a",
        'company_logo': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/a/div/img",
        'company_desc': "//*[@id=\'main-content\']/div/div/div[2]/div[1]/div[2]/div[3]/div[2]/div/div"
    }

    # Initialize Class and validate content on main page
    def __init__(self, driver: object, limit: int = 10):
        log.info("Initialize opening {} web page".format(self.__class__))
        self.__limit = limit
        self.__driver = driver
        try:
            self.__driver.get(self.MAIN_PAGE_URL)
            if self.__driver.title != self.MAIN_PAGE_TITLE:
                raise_exception("Title of page {} has changed: \'{}\'".format(self.JOB_PAGE, self.__driver.title))
            self.wait_loader(True)
            log.info("Loading page done")

        except Exception as e:
            log.error("Exiting job page {} with error: {}".format(self.JOB_PAGE, e))

    def wait_loader(self, is_main_page: bool):
        c = 0
        class_name = 'list-group' if is_main_page else 'job-post-section-title'
        while c < self.__limit:
            try:
                _ = self.__driver.find_element_by_class_name(class_name)
                break
            except:
                log.error("page is still loading")
                time.sleep(1)
                c = c + 1
        if c == self.__limit:
            raise_exception("Unable to open page after {}s".format(self.__limit))

    def find_jobs(self):
        curr_page = 1
        with open('output.txt', 'w') as f:
            print("[", file=f)
        while True:
            time.sleep(0.5)
            jobs = len(self.__driver.find_elements_by_xpath("//h3[@class='job-card-title']/a"))
            for i in range(jobs):
                link = self.get_href_from_list("//h3[@class='job-card-title']/a", i)
                if link == "":
                    continue
                self.open_new_tab(link)
                self.wait_loader(False)
                time.sleep(0.5)

                job_title = self.get_text(self.XPATH['job_title'])
                job_location = self.get_text(self.XPATH['job_location'])
                post_time_str = self.get_text(self.XPATH['job_post_time'])
                post_time = self.get_time_posted(post_time_str)
                salary = self.get_text(self.XPATH['salary'])
                job_type = self.get_text(self.XPATH['job_type'])
                if "0" not in salary:
                    job_type = salary
                    salary = ""
                elif "0" in job_type:
                    salary = job_type
                    job_type = ""

                job_desc = ""
                req_skills = []
                job_category = ""
                for j in range(5):
                    desc_title = self.get_text(self.XPATH['job_desc_title'].format(str(j + 1)))
                    if desc_title == "Job Description":
                        job_desc += "<h2>Job Description</h2>"
                        job_desc += self.get_inner_html(self.XPATH['job_desc_details'].format(str(j + 1)))
                    elif desc_title == "Minimum Qualifications":
                        job_desc += "<h2>Minimum Qualifications</h2>"
                        job_desc += self.get_inner_html(self.XPATH['job_desc_details'].format(str(j + 1)))
                    elif desc_title == "Jobs Summary":
                        job_category = self.get_text(self.XPATH['job_category'].format(str(j + 1)))
                    else:
                        req_skills_title = self.get_text(self.XPATH['req_skills_title'].format(str(j + 1)))
                        if req_skills_title == "Required Skills":
                            skills = self.get_text(self.XPATH['req_skills_details'].format(str(j + 1)))
                            print(self.XPATH['req_skills_details'].format(str(j + 1)))
                            print(skills)
                            req_skills = skills.split('\n')

                company_name = self.get_text(self.XPATH['company_name'])
                company_logo = self.get_img_src(self.XPATH['company_logo'])
                company_about = self.get_text(self.XPATH['company_desc'])

                company_slug = slugify(company_name)
                company = {
                    "name": company_name,
                    "logo": company_logo,
                    "description": company_about,
                    "slug": company_slug,
                    "slug_md5": shorten(make_md5(company_slug)),
                    "platform": "kalibrr",
                }

                job_slug = slugify(job_title)
                job = {
                    "name": job_title,
                    "location": job_location,
                    "salary": salary,
                    "description": job_desc,
                    "contract_type": job_type,
                    "category": job_category,
                    "posted_at": post_time,
                    "required_skills": req_skills,
                    "url": link,
                    "slug": job_slug,
                    "slug_md5": shorten(make_md5(job_slug))
                }
                data = {
                    "job": job,
                    "company": company
                }

                with open('output.txt', 'a') as f:
                    print(ujson.dumps(data)+",", file=f)
                self.close_tab()
            curr_page += 1
            if not self.next_page(curr_page):
                break

    def get_text(self, xpath: str) -> str:
        try:
            val = self.__driver.find_element_by_xpath(xpath)
            return val.text
        except Exception as e:
            return ""

    def get_inner_html(self, xpath: str) -> str:
        try:
            val = self.__driver.find_element_by_xpath(xpath)
            return val.get_attribute('innerHTML')
        except Exception as e:
            return ""

    def get_img_src(self, xpath: str) -> str:
        try:
            val = self.__driver.find_element_by_xpath(xpath)
            return val.get_attribute('src')
        except Exception as e:
            return ""

    def get_href_from_list(self, xpath: str, i: int) -> str:
        try:
            val = self.__driver.find_elements_by_xpath(xpath)[i]
            return val.get_attribute('href')
        except Exception as e:
            return ""

    def open_new_tab(self, link: str):
        self.__driver.execute_script("window.open('');")
        self.__driver.switch_to.window(self.__driver.window_handles[1])
        self.__driver.get(link)

    def close_tab(self):
        self.__driver.close()
        self.__driver.switch_to.window(self.__driver.window_handles[0])

    def next_page(self, page_no: int) -> bool:
        next_page = self.__driver.find_element_by_link_text((str(page_no)))
        if next_page is None:
            return False
        next_page.click()
        return True

    def get_time_posted(self, post_time: str) -> str:
        end = post_time.index("ago") - 1
        s = post_time[len("Posted "):end]
        tokens = s.split(" ")
        val = 0
        if tokens[0] == "a" or tokens[0] == "an":
            val = 1
        else:
            val = int(tokens[0])
        if "minute" in tokens[1]:
            val *= 1
        elif "hour" in tokens[1]:
            val *= 60
        elif "day" in tokens[1]:
            val *= 1440
        elif "month" in tokens[1]:
            val *= 86400
        elif "year" in tokens[1]:
            val *= 31536000
        posted_time = datetime.now() - timedelta(minutes=val)
        return posted_time.strftime("%Y-%m-%d %H:%M:%S")


def raise_exception(msg: str):
    log.error(msg)
    raise Exception(msg)
