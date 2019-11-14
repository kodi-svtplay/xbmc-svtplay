from __future__ import absolute_import
import inspect
import os
import sys
import unittest
# Manipulate path first to add stubs
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lib")

from resources.lib.api import graphql

class TestGraphQLModule(unittest.TestCase):

    def assertItems(self, items):
        self.assertIsNotNone(items)
        self.assertTrue(items)

    def test_getAtoO(self):
        sut = graphql.GraphQL()
        items = sut.getAtoO()
        self.assertItems(items)

    def test_getProgramsByLetter(self):
        sut = graphql.GraphQL()
        items = sut.getProgramsByLetter("A")
        self.assertItems(items)

    def test_getGenres(self):
        sut = graphql.GraphQL()
        items = sut.getGenres()
        self.assertItems(items)
    
    def test_getProgramsForGenres(self):
        sut = graphql.GraphQL()
        items = sut.getProgramsForGenre("animerat")
        self.assertItems(items)
    
    def test_get_episodes(self):
        slug = "agenda"
        sut = graphql.GraphQL()
        items = sut.getVideoContent(slug)
        self.assertItems(items)
  
    def test_get_latest_news(self):
        sut = graphql.GraphQL()
        items = sut.getLatestNews()
        self.assertItems(items)
    
    def test_search_results(self):
        search_term = "agenda"
        sut = graphql.GraphQL()
        items = sut.getSearchResults(search_term)
        self.assertItems(items)
        if len(items) < 1:
            # the hard coded search term needs
            # to be changed if it doesn't yield
            # any results => raise error to alert
            self.fail("search returned no results")

    def test_get_svt_id_for_legacy_id(self):
        """
        This test is using an actual video ID.
        Might break in April 2020... 
        """
        legacy_id = "24186626"
        expected_id = "KABdbpw"
        sut = graphql.GraphQL()
        actual_id = sut.getSvtIdForlegacyId(legacy_id)
        self.assertEqual(actual_id, expected_id)
