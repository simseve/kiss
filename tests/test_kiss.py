#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for KISS Module."""

__author__ = 'Greg Albrecht W2GMD <gba@onbeep.com>'
__copyright__ = 'Copyright 2013 OnBeep, Inc.'
__license__ = 'Apache 2.0'


import unittest

from .context import kiss

from . import constants


class KISSTestCase(unittest.TestCase):

    def setUp(self):
        """Setup."""
        self.test_frames = open(constants.TEST_FRAMES, 'r')
        self.test_frame = self.test_frames.readlines()[0].strip()

    def tearDown(self):
        """Teardown."""
        self.test_frames.close()

    def test_escape_special_codes_fend(self):
        """
        Tests `kiss.util.escape_special_codes` util function.
        """
        fend = kiss.util.escape_special_codes(kiss.constants.FEND)
        self.assertEqual(fend, kiss.constants.FESC_TFEND)

    def test_escape_special_codes_fesc(self):
        """
        Tests `kiss.util.escape_special_codes` util function.
        """
        fesc = kiss.util.escape_special_codes(kiss.constants.FESC)
        self.assertEqual(fesc, kiss.constants.FESC_TFESC)


if __name__ == '__main__':
    unittest.main()