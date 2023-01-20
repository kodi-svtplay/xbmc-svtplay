from __future__ import absolute_import, unicode_literals
import unittest
import sys
import os
# Manipulate path first to add stubs
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lib")

from resources.lib import helper

class TestHelperModule(unittest.TestCase):

    def test_get_url_parameters(self):
        url = "plugin://plugin.video.svtplay?id=http%3A%2F%2Fstream.video%2F%C3%A4.m3u8&mode=video"
        actual = helper.get_url_parameters(url)
        expected = { "id" : "http://stream.video/ä.m3u8", "mode" : "video"}
        self.assertDictEqual(actual, expected)

    def test_strip_html_tags_with_tags(self):
        actual = helper.strip_html_tags('<em>Once upon a time</em>')
        expected = 'Once upon a time'
        self.assertEqual(actual, expected)

    def test_strip_html_tags_without_tags(self):
        actual = helper.strip_html_tags('Once upon a time')
        expected = 'Once upon a time'
        self.assertEqual(actual, expected)

    def test_strip_html_tags_with_None(self):
        actual = helper.strip_html_tags(None)
        expected = None
        self.assertEqual(actual, expected)

if __name__ == "__main__":
  unittest.main()