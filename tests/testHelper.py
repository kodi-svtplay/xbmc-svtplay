from __future__ import absolute_import, unicode_literals
import unittest
import sys
import os
# Manipulate path first to add stubs
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lib")

from resources.lib import helper

class TestHelperModule(unittest.TestCase):

    def test_get_thumb_url(self):
        base_url = "https://www.svtplay.se"
        input_url = "https://www.svtstatic.se/123456/ALTERNATES/medium/affischbild.jpg"
        expected_url = "http://www.svtstatic.se/123456/ALTERNATES/extralarge/affischbild.jpg"
        actual_url = helper.get_thumb_url(input_url, base_url)
        self.assertEqual(actual_url, expected_url)

    def test_get_fanart_url(self):
        base_url = "https://www.svtplay.se"
        input_url = "https://www.svtstatic.se/123456/ALTERNATES/medium/affischbild.jpg"
        expected_url = "http://www.svtstatic.se/123456/ALTERNATES/extralarge_imax/affischbild.jpg"
        actual_url = helper.get_fanart_url(input_url, base_url)
        self.assertEqual(actual_url, expected_url)

if __name__ == "__main__":
  unittest.main()