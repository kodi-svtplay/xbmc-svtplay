import sys
# Manipulate path first
sys.path.append("../")
sys.path.append("./lib")

import resources.lib.svt as svt
import CommonFunctions as common
import inspect

FAIL = "\033[91m"
ENDC = "\033[0m"
OKGREEN = "\033[92m"
BOLD = "\033[1m"

common.plugin = "TestSvt"
common.dbg = True

def runTests(args):
  """
  Run all, defined, tests
  """
  total_fails = 0

  fails = testAtoO()
  total_fails = total_fails + fails

  fails = testCategories()
  total_fails = total_fails + fails

  fails = testProgramsForCategory()
  total_fails = total_fails + fails

  fails = testGetAlphas()
  total_fails = total_fails + fails

  fails = testProgramsByLetter()
  total_fails = total_fails + fails

  fails = testSearchResults()
  total_fails = total_fails + fails

  fails = testGetArticles()
  total_fails = total_fails + fails

  fail_string = OKGREEN + str(total_fails) + ENDC
  if total_fails > 0:
    fail_string = FAIL + str(total_fails) + ENDC
    print(BOLD+"\nTotal fails: "+ENDC+fail_string)
  else:
    print(BOLD+"Tests finished without any errors!"+ENDC)

def testAtoO():

  programs = svt.getAtoO()

  if not programs:
    fail("testAtoO", "No programs!")
    printStats(1)
    return 1

  fails = 0
  for program in programs:
    for key in program.keys():
      if not program[key]:
        fail("testAtoO", "No "+key)
        fails = fails + 1

  printStats(fails)
  return fails

def testCategories():
  
  categories = svt.getCategories()

  if not categories:
    fail("testCargories", "No categories returned!")
    printStats(1)
    return 1
  
  fails = 0
  for category in categories:
    for key in category.keys():
      if not category[key]:
        fail("testCategories", "No "+key)
        fails = fails + 1

  printStats(fails)
  return fails

def testProgramsForCategory():
  
  url = "/barn"

  programs = svt.getProgramsForCategory(url)
  if not programs:
    fail("testProgramsForCategory", "No programs!")
    printStats(1)
    return 1

  fails = 0
  for program in programs:
    for key in program.keys():
      if not program[key]:
        fail("testProgramsForCategory", "No "+key)
        fails = fails + 1

  printStats(fails)
  return fails


def testGetAlphas():

  alphas = svt.getAlphas()

  if not alphas:
    fail("testGetAlphas", "No letters returned!")
    printStats(1)
    return 1

  printStats(0)
  return 0

def testProgramsByLetter():
  
  letter = u'A' # "A" should always have programs...

  programs = svt.getProgramsByLetter(letter)
  if not programs:
    fail("testProgramsByLetter", "No programs!")
    printStats(1)
    return 1

  fails = 0
  for program in programs:
    for key in program.keys():
      if not program[key]:
        fail("testProgramsByLetter", "No "+key)
        fails = fails + 1
  
  printStats(fails)
  return fails


def testSearchResults():

  url = "/sok?q=agenda" # Agenda should have some items

  items = svt.getSearchResults(url)

  if not items:
    fail("testSearchResults", "No items!")
    printStats(1)
    return 1

  fails = 0
  for item in items:
    for key in item.keys():
      if not item[key]:
        fail("testSearchResult", "No "+key)
        fails = fails + 1

  printStats(fails)
  return fails


def testGetArticles():

  fails = 0

  # Test all sections on the frontpage
  for section_name in [svt.SECTION_POPULAR, svt.SECTION_LATEST_VIDEOS, svt.SECTION_LAST_CHANCE]:
    articles = svt.getArticles(section_name)
    if not articles:
      fail("testGetArticles", "No articles for section '"+section_name+"'")
      fails = fails + 1
      continue
    for article in articles:
      for key in article.keys():
        if not article[key]:
          fail("testGetArticles", "No "+key)
          fails = fails + 1

  # Test a program page (Agenda)
  url = "/agenda"
  articles = None
  articles = svt.getArticles(svt.SECTION_EPISODES, url)

  if not articles:
    fail("testGetArticles", "No articles for program page '"+url+"'")
    fails = fails + 1
    printStats(fails)
    return fails

  for article in articles:
    for key in article.keys():
      if not article[key]:
        fail("testGetArticles", "No "+key)
        fails = fails + 1

  printStats(fails)
  return fails

def fail(test_name, message=None):
  print(FAIL+"Test "+test_name+" failed!"+ENDC)
  if message:
    print(BOLD+"Error message: "+ENDC+message)

def printStats(fails):
  name = inspect.stack()[1][3]
  fail_string = OKGREEN + str(fails) + ENDC
  if fails > 0:
    fail_string = FAIL + str(fails) + ENDC
  print("Fails for "+name+": "+fail_string)

if __name__ == "__main__":
  runTests(sys.argv[1:])
