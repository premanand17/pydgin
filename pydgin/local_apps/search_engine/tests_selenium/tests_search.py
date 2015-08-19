from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from django.core.urlresolvers import reverse
from pyvirtualdisplay import Display
from selenium.webdriver.chrome import service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.test import TestCase

BROWSERS = []
HOST = "http://tim-rh3:8000"


def setUpModule():
    global BROWSER
    display = Display(visible=0, size=(1000, 800))
    display.start()
    BROWSERS.append(webdriver.Firefox())
    BROWSERS.append(webdriver.Chrome())

#     webdriver_service = service.Service("/gdxbase/www/tim-dev/operadriver", 9315)
#     desired_caps = {}
#     desired_caps['automationName'] = 'selendroid'
#     desired_caps['platformName'] = 'Android'
#     desired_caps['deviceName'] = ''
#     desired_caps['chromedriverExecutable'] = "/gdxbase/www/tim-dev/operadriver"
#     desired_caps['appPackage'] = 'com.opera.browser'
#     driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', desired_caps)
#     BROWSERS.append(webdriver.Opera())


def tearDownModule():
    # Call tearDown to close the web browser
    for br in BROWSERS:
        br.quit()


class Search(TestCase):

    def test_search_box_autosuggest(self):
        ''' Test auto-suggest '''
        for br in BROWSERS:
            br.get(HOST+reverse('search_page'))
            time.sleep(0.2)

            search_box = br.find_element_by_name("query")
            if not search_box.is_displayed():
                navbar = br.find_element_by_class_name("navbar-toggle")
                navbar.click()
                time.sleep(0.2)

            auto_complete = br.find_element_by_class_name("ui-autocomplete")

            search_box.send_keys("PT")
            time.sleep(0.4)
            self.assertTrue(auto_complete.is_displayed())

    def test_search_box(self):
        ''' Test searching. '''
        for br in BROWSERS:
            br.get(HOST+reverse('search_page'))
            search_box = br.find_element_by_name("query")
            if not search_box.is_displayed():
                navbar = br.find_element_by_class_name("navbar-toggle")
                navbar.click()
                time.sleep(0.2)
            search_box.send_keys("PTN22")
            search_box.send_keys(Keys.RETURN)
