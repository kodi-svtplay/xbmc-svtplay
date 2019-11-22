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

    def test_get_url_parameters(self):
        url = "plugin://plugin.video.svtplay?url=http%3A%2F%2Fstream.video%2F%C3%A4.m3u8&mode=video"
        actual = helper.get_url_parameters(url)
        expected = { "url" : "http://stream.video/ä.m3u8", "mode" : "video"}
        self.assertDictEqual(actual, expected)

    def test_episode_url_to_show_url(self):
        url = "/video/22132986/some-thing-here/abel-och-fant-sasong-2-kupa-pa-rymmen"
        actual = helper.episodeUrlToShowUrl(url)
        expected = "/some-thing-here"
        self.assertEqual(actual, expected)

    def test_single_video_url_to_show_url(self):
        url = "/video/22132986/some-thing-here"
        actual = helper.episodeUrlToShowUrl(url)
        self.assertIsNone(actual)

if __name__ == "__main__":
  unittest.main()