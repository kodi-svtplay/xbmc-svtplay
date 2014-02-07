# -*- coding: utf-8 -*-
import CommonFunctions
import re
import resources.lib.helper as helper
import urllib

common = CommonFunctions

BASE_URL = "http://beta.svtplay.se"
SWF_URL = "http://www.svtplay.se/public/swf/video/svtplayer-2013.05.swf"

BANDWIDTH = [300, 500, 900, 1600, 2500, 5000]

URL_A_TO_O = "/program"
URL_TO_SEARCH = "/sok?q="
URL_TO_OA = "/kategorier/oppetarkiv"
JSON_SUFFIX = "?output=json"

SECTION_POPULAR = "popular-videos"
SECTION_LATEST_VIDEOS = "latest-videos"
SECTION_LAST_CHANCE = "last-chance-videos"
SECTION_BROADCAST = "live-channels"
SECTION_LATEST_CLIPS = "latest-clips"
SECTION_EPISODES = "more-episodes"

SEARCH_LIST_TITLES = "[^\"']*playJs-search-titles[^\"']*"
SEARCH_LIST_EPISODES = "[^\"']*playJs-search-episodes[^\"']*" 
SEARCH_LIST_CLIPS = "[^\"']*playJs-search-clips[^\"']*" 


def getAtoO():
  """
  Returns a list of all programs, sorted A-Z.
  """
  html = getPage(URL_A_TO_O)

  linkClass = "play-alphabetic-link"
  texts = common.parseDOM(html, "a" , attrs = { "class": linkClass })
  hrefs = common.parseDOM(html, "a" , attrs = { "class": linkClass }, ret = "href")
  
  programs = []

  for index, text in enumerate(texts):
    program = {}
    program["title"] = common.replaceHTMLCodes(text)
    program["url"] = hrefs[index]
    programs.append(program)

  return programs


def getCategories():
  """
  Returns a list of all categories.
  """
  html = getPage("/")

  container = common.parseDOM(html, "div", attrs = { "id": "[^\"']*playJs-categories[^\"']*" })

  articles = common.parseDOM(container, "article")

  categories = []

  for article in articles:
    category = {}
    category["url"] = common.parseDOM(article, "a", ret = "href")[0]
    title = common.parseDOM(article, "h2")[0]

    if category["url"].endswith("oppetarkiv"):
      # Skip the "Oppetarkiv" category
      continue

    category["title"] = common.replaceHTMLCodes(title)
    categories.append(category)

  return categories


def getProgramsForCategory(url):
  html = getPage(url)

  container = common.parseDOM(html, "div", attrs = { "class" : "[^\"']*play-alphabetic-list-titles[^\"']*" })

  if not container:
    common.log("Could not find container for URL "+url)
    return None

  lis = common.parseDOM(container, "li", attrs = { "class" : "[^\"']*play-list-item[^\"']*" })

  if not lis:
    common.log("Could not find program links for URL "+url)
    return None
  
  programs = []

  for li in lis:
    href = common.parseDOM(li, "a", ret = "href")[0]
    title = common.parseDOM(li, "a")[0]
    program = {}
    program["title"] = common.replaceHTMLCodes(title)
    program["url"] = href
    programs.append(program)

  return programs


def getAlphas():
  """
  Returns a list of all letters in the alphabet that 
  matches the starting letter of some program.
  """
  html = getPage(URL_A_TO_O)
  container = common.parseDOM(html, "div", attrs = { "class" : "[^\"']*play-alphabetic-list-titles[^\"']*" })

  if not container:
    common.log("No container found!")
    return None

  letters = common.parseDOM(container[0], "h3", attrs = { "class" : "[^\"']*play-alphabetic-heading[^\"']*" })

  if not letters:
    common.log("Could not find any letters!")
    return None

  alphas = []

  for letter in letters:
    alpha = {}
    alpha["title"] = helper.convertChar(letter)
    alpha["char"] =  letter
    alphas.append(alpha)

  return alphas


def getProgramsByLetter(letter):
  """
  Returns a list of all program starting with the supplied letter.
  """
  letter = urllib.unquote(letter)

  html = getPage(URL_A_TO_O)

  letterboxes = common.parseDOM(html, "div", attrs = { "class": "[^\"']*play-alphabetic-letter[^\"']*" })

  for letterbox in letterboxes:

    heading = common.parseDOM(letterbox, "h3")[0]

    if heading == letter:
      break

  lis = common.parseDOM(letterbox, "li", attrs = { "class": "[^\"']*play-list-item[^\"']*" })

  programs = []

  for li in lis:
    program = {}
    program["url"] = common.parseDOM(li, "a", ret = "href")[0]
    title = common.parseDOM(li, "a")[0]
    program["title"] = common.replaceHTMLCodes(title)
    programs.append(program)
    
  return programs

def getSearchResults(url):
  """

  """
  html = getPage(url)

  results = []

  for listId in [SEARCH_LIST_TITLES, SEARCH_LIST_EPISODES, SEARCH_LIST_CLIPS]:
    items = getSearchResultsForList(html, listId)
    if not items:
      common.log("No items in list '"+listId+"'")
    results.extend(items)

  return results


def getSearchResultsForList(html, listId):
  """

  """
  container = common.parseDOM(html, "div", attrs = { "id" : listId })
  if not container:
    common.log("No container found for list ID '"+listId+"'")
    return None

  articles = common.parseDOM(container, "article")
  if not articles:
    common.log("No articles found for list ID '"+listId+"'")
    return None

  titles = common.parseDOM(container, "article", ret = "data-title")
  
  results = []
  for index, article in enumerate(articles):
    thumbnail = common.parseDOM(article, "img", attrs = { "class" : "[^\"']*play-videolist-thumbnail[^\"']*" }, ret = "src")[0]
    url = common.parseDOM(article, "a", ret = "href")[0]
    title = common.replaceHTMLCodes(titles[index])
    thumbnail = helper.prepareThumb(thumbnail)

    itemType = "video"
    if listId == SEARCH_LIST_TITLES:
      itemType = "program"
    results.append({"item": { "title" : title, "thumbnail" : thumbnail, "url" : url  }, "type" : itemType })

  return results


def getArticles(sectionName, url=None):
  """

  """
  if not url:
    url = "/"
  html = getPage(url)

  videoListClass = "[^\"']*play-videolist" 
  containers = common.parseDOM(html, "div", attrs = { "class" : videoListClass })

  if not containers:
    common.log("Could not find container for "+sectionName)
    return None

  ids = common.parseDOM(html, "div", attrs = { "class" : videoListClass }, ret = "id")

  if not ids:
    common.log("Could not find IDs for "+sectionName)
    return None

  container = None
  for index, section in enumerate(containers):
    if ids[index] == sectionName:
      #Found right section, use for articles
      container = section
      break
  
  if not container:
    common.log("No section found matching '"+sectionName+"' !")
    return None
  
  articleClass = "[^\"']*play-videolist-element[^\"']*"
  articles = common.parseDOM(container, "article", attrs = { "class" : articleClass })
  titles = common.parseDOM(container, "article", attrs = { "class" : articleClass }, ret = "data-title")
  plots = common.parseDOM(container, "article", attrs = { "class" : articleClass }, ret = "data-description")
  airtimes = common.parseDOM(container, "article", attrs = { "class" : articleClass }, ret = "data-broadcasted")
  durations = common.parseDOM(container, "article", attrs = { "class" : articleClass }, ret = "data-length")
  newarticles = []
  
  if not articles:
    common.log("No articles found for section '"+sectionName+"' !")
    return None
 
  for index, article in enumerate(articles):
    info = {}
    newarticle = {}
    plot = plots[index]
    aired = airtimes[index]
    duration = durations[index]
    title = titles[index]
    newarticle["url"] = common.parseDOM(article, "a",
                            attrs = { "class": "[^\"']*play-videolist-element-link[^\"']*" },
                            ret = "href")[0]
    thumbnail = common.parseDOM(article,
                                "img",
                                attrs = { "class": "[^\"']*play-videolist-thumbnail[^\"']*" },
                                ret = "src")[0]
    newarticle["thumbnail"] = helper.prepareThumb(thumbnail)
    
    title = common.replaceHTMLCodes(title)
    plot = common.replaceHTMLCodes(plot)
    aired = common.replaceHTMLCodes(aired) 
    newarticle["title"] = title
    info["title"] = title
    info["plot"] = plot
    info["aired"] = aired
    info["duration"] = helper.convertDuration(duration)
    newarticle["info"] = info
    newarticles.append(newarticle)
 
  return newarticles


def getPage(url):
  """
  Wrapper, calls helper.getPage
  """
  return helper.getPage(BASE_URL + url) 

def getHighBw(low):
  """
  Returns the higher bandwidth boundary
  """
  i = BANDWIDTH.index(low)
  return BANDWIDTH[i+1]
