from __future__ import absolute_import
import inspect
import os
import sys
import unittest
# Manipulate path first to add stubs
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lib")

from resources.lib.api import graphql

class TestGraphQLModule(unittest.TestCase):

    def test_getAtoO(self):
        sut = graphql.GraphQL()
        items = sut.getAtoO()
        self.assertIsNotNone(items)

    def test_getProgramsByLetter(self):
        sut = graphql.GraphQL()
        items = sut.getProgramsByLetter("A")
        self.assertIsNotNone(items)
