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