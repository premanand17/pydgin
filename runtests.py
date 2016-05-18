#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pydgin.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    settings.TESTMODE = True
    failures = test_runner.run_tests([
        # 'auth_test.tests',
        'core.tests',
        'disease.tests',
        'elastic.tests',
        'gene.tests',
        'marker.tests',
        'pydgin_auth.tests',
        'pydgin.tests',
        'region.tests',
        'search_engine.tests',
        'study.tests'])
    sys.exit(bool(failures))
