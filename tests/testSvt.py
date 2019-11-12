from __future__ import absolute_import
import inspect
import os
import sys
import unittest
# Manipulate path first to add stubs
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lib")

from resources.lib.api import svt

class TestSvtModule(unittest.TestCase):

  def assertHasContent(self, list):
    if list == None:
      self.fail("List is None")
      return False
    return True

  def assertHasContentStrict(self, list):
    if list == None:
      self.fail("List is None")
    if len(list) < 1:
      self.fail("List is empty")

  def test_get_alphas(self):
    alphas = svt.getAlphas()
    self.assertHasContentStrict(alphas)

  def test_search_results(self):
    search_term = "agenda"
    items = svt.getSearchResults(search_term)
    self.assertHasContent(items)
    if len(items) < 1:
        # the hard coded search term needs
        # to be changed if it doesn't yield
        # any results => raise error to alert
        self.fail("search returned no results")
    for item in items:
      for key in item.keys():
        self.assertIsNotNone(item[key])

  def test_get_channels(self):
    items = svt.getChannels()
    self.assertHasContentStrict(items)

  def test_get_latest_items(self):
    (items, _) = svt.getItems("latest", 1)
    for item in items:
      self.assertHasContent(item)

  def test_get_popular(self):
    (items, _) = svt.getItems("popular", 1)
    for item in items:
      self.assertHasContent(item)

  def test_get_last_chance(self):
    (items, _) = svt.getItems("last_chance", 1)
    for item in items:
      self.assertHasContent(item)

  def test_get_video_json(self):
    items = svt.getAtoO()
    self.assertHasContent(items)
    video_ok = False
    for item in items:
      if video_ok:
        break
      if item["type"] != "program":
          continue
      slug = item["url"].split("/")[-1]
      episodes = svt.getEpisodes(slug)
      self.assertHasContent(episodes)
      for episode in episodes:
        json_obj = svt.getVideoJSON(episode["url"])
        if self.assertHasContent(json_obj):
          video_ok = True
          break

if __name__ == "__main__":
  unittest.main()
