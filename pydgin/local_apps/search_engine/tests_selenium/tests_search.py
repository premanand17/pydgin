''' Test JS in search engine app. '''
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
BROWSERS = []
BROWSERS_SIZES = [[414, 736], [1000, 800]]

SELENIUM = getattr(settings, 'SELENIUM', {})
logger.debug(SELENIUM)
HEADLESS = SELENIUM.get('HEADLESS', True)
HOST = SELENIUM.get('HOST', "http://localhost:8000")


def setUpModule():
    ''' Open browsers for testing. '''
    global BROWSER

    if HEADLESS:
        logger.debug("HEADLESS MODE")
        display = Display(visible=0, size=(1000, 800))
        display.start()

    logger.debug(SELENIUM)
    BROWSERS.append(webdriver.Firefox())
    BROWSERS.append(webdriver.Chrome(SELENIUM.get('CHROME_DRIVER', "")))
    BROWSERS.append(_get_opera_driver())
    logger.debug("setUpModule DONE")


def tearDownModule():
    ''' Close web browsers. '''
    for br in BROWSERS:
        br.quit()


def _get_opera_driver():
    ''' Use OperaChromiumDriver for Opera testing.
    L{https://github.com/operasoftware/operachromiumdriver}
    L{https://github.com/operasoftware/operachromiumdriver/blob/master/docs/python-setup-step-by-step.md}
    L{https://github.com/operasoftware/operachromiumdriver/blob/master/docs/desktop.md}
    '''
    logger.debug("GET OPERA DRIVER")
    webdriver_service = service.Service(SELENIUM.get('OPERA_DRIVER', ""))
    webdriver_service.start()
    desired_caps = DesiredCapabilities.OPERA
    desired_caps['operaOptions'] = {'binary': SELENIUM.get('OPERA_BIN', "/usr/bin/opera")}
    logger.debug("GET OPERA DRIVER DONE")
    return webdriver.Remote(webdriver_service.service_url, desired_caps)


class Search(TestCase):

    def test_search_box_autosuggest(self):
        ''' Test auto-suggest '''
        for br in BROWSERS:
            for br_size in BROWSERS_SIZES:
                br.set_window_size(br_size[0], br_size[1])

                br.get(HOST+reverse('search_page'))
                time.sleep(0.2)

                search_box = br.find_element_by_name("query")
                if not search_box.is_displayed():
                    self.assertLess(br_size[0], 768)  # bootstrap breakpoints at which your layout will change
                    navbar = br.find_element_by_class_name("navbar-toggle")
                    navbar.click()
                    time.sleep(0.2)

                auto_complete = br.find_element_by_class_name("ui-autocomplete")
                search_box.send_keys("PT")
                time.sleep(1)
                self.assertTrue(auto_complete.is_displayed())

    def test_search_box(self):
        ''' Test searching. '''
        for br in BROWSERS:
            for br_size in BROWSERS_SIZES:
                br.set_window_size(br_size[0], br_size[1])

                br.get(HOST+reverse('search_page'))
                search_box = br.find_element_by_name("query")
                if not search_box.is_displayed():
                    self.assertLess(br_size[0], 768)  # bootstrap breakpoints at which your layout will change
                    navbar = br.find_element_by_class_name("navbar-toggle")
                    navbar.click()
                    time.sleep(1)
                search_box.send_keys("PTPN22")
                search_box.send_keys(Keys.RETURN)
                time.sleep(1)
                self.assertTrue("hit(s) for 'PTPN22':" in br.page_source)
