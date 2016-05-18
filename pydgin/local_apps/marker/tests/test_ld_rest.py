''' Test for LD rest interface. '''
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from pyRserve.rexceptions import RConnectionRefused
from rest_framework import status


class LDRestTest(TestCase):

    def test_ld_list(self):
        ''' Test retrieving markers in LD of given marker. '''
        url = reverse('rest:ld-list') + "?format=json&m1=rs10774624"
        try:
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            ld = json.loads(response.content.decode("utf-8"))[0]['ld']
            self.assertGreater(len(ld), 0, 'results found')
        except (RConnectionRefused, KeyError):
            pass
