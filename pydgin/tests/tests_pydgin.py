''' Pydgin global tests. '''
from builtins import classmethod

from django.core.urlresolvers import reverse
from django.test import TestCase
import ftplib
import ftputil
import requests

from elastic.elastic_settings import ElasticSettings
from urllib.parse import urlparse
import re


class PydginTest(TestCase):

    def test_url(self):
        ''' Test the search page. '''
        url = reverse('search_page')
        self.assertEqual(url, '/search/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_settings(self):
        ''' Test elastic server is running. '''
        resp = requests.get(ElasticSettings.url())
        self.assertEqual(resp.status_code, 200)


class PydginTestUtils():

    @classmethod
    def test_links_in_page(cls, test_case, url, data={}):
        resp = test_case.client.get(url, data)
        content = resp.content.decode("utf-8")
        body = content[content.find('<body>'):content.find('<footer>')]

        # remove scripts from body
        parts = body.split('script>')
        i = 0
        txt = ''
        for part in parts:
            if i % 3 == 1:
                txt += part
            i += 1

        data = txt.split("</a>")
        tag = "<a href=\""
        endtag = "\""
        for item in data:
            if "<a href" in item:
                try:
                    ind = item.index(tag)
                    item = item[ind+len(tag):]
                    end = item.index(endtag)
                except:
                    pass
                else:
                    path = item[:end]
                    if path == '#':
                        continue
                    elif re.match('^/|http|ftp|'+url, path):
                        link_url = path
                    else:
                        link_url = url + path

                    if link_url.startswith('http'):
                        resp = requests.get(link_url)
                    elif link_url.startswith('ftp'):
                        test_case.assertTrue(PydginTestUtils.ftp_exists(link_url), msg=link_url)
                        continue
                    else:
                        resp = test_case.client.get(link_url)
                    test_case.assertEqual(resp.status_code, 200, msg=link_url)

    @classmethod
    def ftp_exists(cls, url, username='anonymous', password=''):
        url_parse = urlparse(url)
        ftp_host = ftputil.FTPHost(url_parse.netloc, username, password,
                                   session_factory=ftplib.FTP)
        return ftp_host.path.exists(url_parse.path)
