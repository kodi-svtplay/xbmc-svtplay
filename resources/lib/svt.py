# -*- coding: utf-8 -*-
import urllib
import resources.lib.helper as helper
import CommonFunctions as common

BASE_URL = "http://beta.svtplay.se"
SWF_URL = "http://www.svtplay.se/public/swf/video/svtplayer-2013.05.swf"

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

  link_class = "[^\"']*play_alphabetic-link[^\"']*"
  texts = common.parseDOM(html, "a" , attrs = { "class": link_class })
  hrefs = common.parseDOM(html, "a" , attrs = { "class": link_class }, ret = "href")
  
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
  """
  Returns a list of programs for a specific category URL.
  """
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
  Returns a list of all letters in the alphabet that has programs.
  """
  html = getPage(URL_A_TO_O)
  container = common.parseDOM(html, "div", attrs = { "class" : "[^\"']*play-alphabetic-list-titles[^\"']*" })

  if not container:
    common.log("No container found!")
    return None

  letters = common.parseDOM(container[0], "h3", attrs = { "class" : "[^\"']*play-alphabetic-letter--title[^\"']*" })

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
  letterbox = None

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
  Returns a list of both clips and programs
  for the supplied search URL.
  """
  html = getPage(url)

  results = []

  for list_id in [SEARCH_LIST_TITLES, SEARCH_LIST_EPISODES, SEARCH_LIST_CLIPS]:
    items = getSearchResultsForList(html, list_id)
    if not items:
      common.log("No items in list '"+list_id+"'")
    results.extend(items)

  return results


def getSearchResultsForList(html, list_id):
  """
  Returns the items in the supplied list.

  Lists are the containers on a program page that contains clips or programs.
  """
  container = common.parseDOM(html, "div", attrs = { "id" : list_id })
  if not container:
    common.log("No container found for list ID '"+list_id+"'")
    return None

  articles = common.parseDOM(container, "article")
  if not articles:
    common.log("No articles found for list ID '"+list_id+"'")
    return None

  titles = common.parseDOM(container, "article", ret = "data-title")
  
  results = []
  for index, article in enumerate(articles):
    thumbnail = common.parseDOM(article, "img", attrs = { "class" : "[^\"']*play-videolist-thumbnail[^\"']*" }, ret = "src")[0]
    url = common.parseDOM(article, "a", ret = "href")[0]
    title = common.replaceHTMLCodes(titles[index])
    thumbnail = helper.prepareThumb(thumbnail)

    item_type = "video"
    if list_id == SEARCH_LIST_TITLES:
      item_type = "program"
    results.append({"item": { "title" : title, "thumbnail" : thumbnail, "url" : url  }, "type" : item_type })

  return results


def getArticles(section_name, url=None):
  """
  Returns a list of the articles ina section as program items.

  Program items has 'title', 'thumbnail', 'url' and 'info' keys.
  """
  if not url:
    url = "/"
  html = getPage(url)

  video_list_class = "[^\"']*play-videolist" 
  containers = common.parseDOM(html, "div", attrs = { "class" : video_list_class })

  if not containers:
    common.log("Could not find container for "+section_name)
    return None

  ids = common.parseDOM(html, "div", attrs = { "class" : video_list_class }, ret = "id")

  if not ids:
    common.log("Could not find IDs for "+section_name)
    return None

  container = None
  for index, section in enumerate(containers):
    if ids[index] == section_name:
      #Found right section, use for articles
      container = section
      break
  
  if not container:
    common.log("No section found matching '"+section_name+"' !")
    return None
  
  article_class = "[^\"']*play-videolist-element[^\"']*"
  articles = common.parseDOM(container, "article", attrs = { "class" : article_class })
  titles = common.parseDOM(container, "article", attrs = { "class" : article_class }, ret = "data-title")
  plots = common.parseDOM(container, "article", attrs = { "class" : article_class }, ret = "data-description")
  airtimes = common.parseDOM(container, "article", attrs = { "class" : article_class }, ret = "data-broadcasted")
  durations = common.parseDOM(container, "article", attrs = { "class" : article_class }, ret = "data-length")
  new_articles = []
  
  if not articles:
    common.log("No articles found for section '"+section_name+"' !")
    return None
 
  for index, article in enumerate(articles):
    info = {}
    new_article = {}
    plot = plots[index]
    aired = airtimes[index]
    duration = durations[index]
    title = titles[index]
    new_article["url"] = common.parseDOM(article, "a",
                            attrs = { "class": "[^\"']*play-videolist-element-link[^\"']*" },
                            ret = "href")[0]
    thumbnail = common.parseDOM(article,
                                "img",
                                attrs = { "class": "[^\"']*play-videolist-thumbnail[^\"']*" },
                                ret = "src")[0]
    new_article["thumbnail"] = helper.prepareThumb(thumbnail)
    
    title = common.replaceHTMLCodes(title)
    plot = common.replaceHTMLCodes(plot)
    aired = common.replaceHTMLCodes(aired) 
    new_article["title"] = title
    info["title"] = title
    info["plot"] = plot
    info["aired"] = aired
    info["duration"] = helper.convertDuration(duration)
    new_article["info"] = info
    new_articles.append(new_article)
 
  return new_articles

def getVideoUrl(json_obj):
  """
  Returns the video URL from a SVT JSON object.
  """
  url = None

  for video in json_obj["video"]["videoReferences"]:
    if video["playerType"] == "ios":
      url = video["url"]

  return url

def getSubtitleUrl(json_obj):
  """
  Returns a subtitleURL from a SVT JSON object.
  """
  url = None

  for subtitle in json_obj["video"]["subtitleReferences"]:
    if subtitle["url"].endswith(".wsrt"):
      url = subtitle["url"]
    else:
      if len(subtitle["url"]) > 0:
        common.log("Skipping unknown subtitle: " + subtitle["url"])
  
  return url


def getPage(url):
  """
  Wrapper, calls helper.getPage with SVT's base URL
  """
  return helper.getPage(BASE_URL + url) 
