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
        items = sut.getEpisodes(slug)
        self.assertItems(items)
  
    def test_get_latest_news(self):
        sut = graphql.GraphQL()
        items = sut.getLatestNews()
        self.assertItems(items)