import inspect
import sys
import unittest
# Manipulate path first
sys.path.append("../")
sys.path.append("./lib")

import resources.lib.svt as svt
import CommonFunctions as common

# Set up the CommonFunctions module
common.plugin = "TestSvt"
common.dbg = True

class TestSvtModule(unittest.TestCase):

  def test_alphabetic(self):
    """
    Verifies tbat svt.getAtoO() returns programs 
    and that there are no empty attributes.
    """
    programs = svt.getAtoO()

    self.assertIsNotNone(programs)

    for program in programs:
      for key in program.keys():
        self.assertIsNotNone(program[key])



  def test_categories(self):
    
    categories = svt.getCategories()

    self.assertIsNotNone(categories)

    for category in categories:
      for key in category.keys():
        self.assertIsNotNone(category[key])

  def test_programs_for_category(self):
   
    # Use the "Barn" category since is changes a lot
    url = "/barn"

    programs = svt.getProgramsForCategory(url)
    
    self.assertIsNotNone(programs)

    for program in programs:
      for key in program.keys():
        self.assertIsNotNone(program[key])

  def test_get_alphas(self):

    alphas = svt.getAlphas()

    self.assertIsNotNone(alphas)

  def test_programs_by_letter(self):
    
    letter = u'A' # "A" should always have programs...

    programs = svt.getProgramsByLetter(letter)
    self.assertIsNotNone(programs)

    for program in programs:
      for key in program.keys():
        self.assertIsNotNone(program[key])

  def test_search_results(self):

    url = "/sok?q=agenda" # Agenda should have some items

    items = svt.getSearchResults(url)

    self.assertIsNotNone(items)

    for item in items:
      for key in item.keys():
        self.assertIsNotNone(item[key])

  def test_get_articles(self):

    section_names = [
        svt.SECTION_POPULAR, 
        svt.SECTION_LATEST_VIDEOS, 
        svt.SECTION_LAST_CHANCE, 
        svt.SECTION_LIVE_CHANNELS
        ] 

    # Test all sections on the frontpage
    for section_name in section_names:
      articles = svt.getArticles(section_name)
      
      self.assertIsNotNone(articles)

      for article in articles:
        for key in article.keys():
          self.assertIsNotNone(article[key])

    # Test a program page (Agenda)
    url = "/agenda"
    articles = None
    articles = svt.getArticles(svt.SECTION_EPISODES, url)

    self.assertIsNotNone(articles)

    for article in articles:
      for key in article.keys():
        self.assertIsNotNone(article[key])

if __name__ == "__main__":
  unittest.main()
