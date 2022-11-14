from __future__ import absolute_import

import unittest
import os
import sys 

# Manipulate path first to add stubs for xbmc libs
curr_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_path + "/lib")

from resources.lib.svtplay import SvtPlay
import xbmcplugin

class TestSvtPlay(unittest.TestCase):

    def tearDown(self):
        xbmcplugin.clearDirectoryItems()

    def assertDirectoryHasItems(self):
        items = xbmcplugin.getDirectoryItems()
        self.assertGreater(len(items), 0, "No directory items found")

    def assertDirectoryIsEmpty(self):
        self.assertEquals(len(xbmcplugin.getDirectoryItems()), 0)

    def test_view_a_to_z_and_select_random_item(self):
        sut = SvtPlay(plugin_handle="testhandle", plugin_url="testurl")
        plugin_params = "?mode={}".format(sut.MODE_A_TO_O)
        sut.run(plugin_params)
        self.assertDirectoryHasItems()
        item = xbmcplugin.getRandomDirectoryItem()
        (url, _, isFolder) = item
        xbmcplugin.clearDirectoryItems()
        sut.run(url)
        if isFolder:
            self.assertDirectoryHasItems()
        else:
            self.assertTrue("m3u8" in xbmcplugin.getResolvedListItemPath(), "Path is not a m3u8 playlist")
