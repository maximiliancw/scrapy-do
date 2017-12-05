#-------------------------------------------------------------------------------
# Author: Lukasz Janyst <lukasz@jany.st>
# Date:   05.12.2017
#
# Licensed under the 3-Clause BSD License, see the LICENSE file for details.
#-------------------------------------------------------------------------------

import tempfile
import shutil
import os

from twisted.internet.defer import inlineCallbacks
from scrapy_do.controller import Controller
from unittest.mock import Mock, patch, DEFAULT
from twisted.trial import unittest


#-------------------------------------------------------------------------------
class ControllerTests(unittest.TestCase):

    #---------------------------------------------------------------------------
    def test_setup(self):
        temp_dir = tempfile.mkdtemp()
        config = Mock()
        config.get_string.return_value = temp_dir
        Controller(config)  # no metadata file
        Controller(config)  # metadata file exists
        shutil.rmtree(temp_dir)

    #---------------------------------------------------------------------------
    @inlineCallbacks
    def test_push_project(self):
        #-----------------------------------------------------------------------
        # Set up
        #-----------------------------------------------------------------------
        temp_dir = tempfile.mkdtemp()
        config = Mock()
        config.get_string.return_value = temp_dir
        controller = Controller(config)

        with open('tests/quotesbot.zip', 'rb') as f:
            data = f.read()

        with open('tests/broken-proj.zip', 'rb') as f:
            broken_data = f.read()

        #-----------------------------------------------------------------------
        # Configure the error cases tests
        #-----------------------------------------------------------------------
        def chk_unzip(e):
            self.assertEqual(str(e), 'Not a valid zip archive')
        unzip_error = {
            'name': 'test',
            'data': b'foo',
            'exc_check': chk_unzip
        }

        def chk_name(e):
            self.assertTrue(str(e).startswith('Project'))
        name_error = {
            'name': 'test',
            'data': broken_data,
            'exc_check': chk_name
        }

        def chk_list(e):
            self.assertEqual(str(e), 'Unable to get the list of spiders')
        list_error = {
            'name': 'broken-proj',
            'data': broken_data,
            'exc_check': chk_list
        }

        error_params = [unzip_error, name_error, list_error]

        #-----------------------------------------------------------------------
        # Test the error cases
        #-----------------------------------------------------------------------
        for params in error_params:
            temp_test_dir = tempfile.mkdtemp()
            temp_test_file = tempfile.mkstemp()
            with patch.multiple('tempfile',
                                mkstemp=DEFAULT, mkdtemp=DEFAULT) as mock:
                mock['mkdtemp'].return_value = temp_test_dir
                mock['mkstemp'].return_value = temp_test_file

                try:
                    yield controller.push_project(params['name'],
                                                  params['data'])
                    self.assertFail()
                except ValueError as e:
                    params['exc_check'](e)

                self.assertFalse(os.path.exists(temp_test_dir))
                self.assertFalse(os.path.exists(temp_test_file[1]))

        #-----------------------------------------------------------------------
        # Test the correct case
        #-----------------------------------------------------------------------
        temp_test_dir = tempfile.mkdtemp()
        temp_test_file = tempfile.mkstemp()
        with patch.multiple('tempfile',
                            mkstemp=DEFAULT, mkdtemp=DEFAULT) as mock:
            mock['mkdtemp'].return_value = temp_test_dir
            mock['mkstemp'].return_value = temp_test_file

            spiders = yield controller.push_project('quotesbot', data)
            self.assertFalse(os.path.exists(temp_test_dir))
            self.assertFalse(os.path.exists(temp_test_file[1]))
            self.assertIn('toscrape-css', spiders)
            self.assertIn('toscrape-xpath', spiders)

        #-----------------------------------------------------------------------
        # Clean up
        #-----------------------------------------------------------------------
        shutil.rmtree(temp_dir)