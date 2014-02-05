# -*- coding: utf-8 -*-
import CommonFunctions
import re
import helper
import urllib

common = CommonFunctions

BASE_URL = "http://beta.svtplay.se"
SWF_URL = "http://www.svtplay.se/public/swf/video/svtplayer-2013.05.swf"

BANDWIDTH = [300,500,900,1600,2500,5000]

URL_A_TO_O = "/program"
URL_CATEGORIES = "/program"
URL_CHANNELS = "/kanaler"
URL_TO_LATEST = "?tab=senasteprogram&sida=1"
URL_TO_LATEST_NEWS = "?tab=senastenyhetsprogram&sida=1"
URL_TO_RECOMMENDED = "?tab=rekommenderat&sida=1"
URL_TO_SEARCH = "/sok?q="
URL_TO_LIVE = "/ajax/live"
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

CLASS_SHOW_MORE_BTN = "[^\"']*playShowMoreButton[^\"']*"
DATA_NAME_SHOW_MORE_BTN = "sida"

TAB_TITLES      = "titlar"
TAB_EPISODES    = "program"
TAB_LATEST      = "senasteprogram"
TAB_CLIPS       = "klipp"
TAB_NEWS        = "senastenyhetsprogram"
TAB_RECOMMENDED = "rekommenderat"

TAB_S_TITLES    = "titles"
TAB_S_CLIPS     = "clips"
TAB_S_EPISODES  = "episodes"

def getChannels():
  """
  Returns a list of all availble live channels  
  """
  html = getPage(URL_CHANNELS)

  container = common.parseDOM(html, "ul", attrs = { "data-player":"player" })[0]

  lis = common.parseDOM(container, "li")

  channels = []

  for li in lis:
    chname = common.parseDOM(li, "a", ret = "title")[0]
    thumbnail = common.parseDOM(li, "a", ret = "data-thumbnail")[0]
    url = common.parseDOM(li, "a", ret = "href")[0]
    prname = common.parseDOM(li, "span", attrs = { "class":"[^\"']*playChannelMenuTitle[^\"']*"})[0]
    chname = re.sub("\S*\|.*","| ",chname)
    title = chname + prname
    title = common.replaceHTMLCodes(title)
    thumbnail = helper.prepareThumb(thumbnail)
    channels.append({"title":title,"url":url,"thumbnail":thumbnail})

  return channels


def getLivePrograms():
  """
  Returns the programs that are live now
  """
  html = getPage(URL_TO_LIVE)
  
  container = common.parseDOM(html, "section", attrs = { "class": "svtUnit svtNth-1"})[0]

  lis = common.parseDOM(container, "li", attrs = { "class": "[^\"']*svtMediaBlock[^\"']*" })
  articles = []
 
  for li in lis:

    # Look for the live icon/marker. If it exist for li then create directory item
    liveIcon = common.parseDOM(li, "img", attrs = { "class": "[^\"']*playBroadcastLiveIcon[^\"']*"})

    if len(liveIcon) > 0:

      title = common.parseDOM(li, "h1")[0]
      url = common.parseDOM(li, "a", ret = "href")[0]
      thumbnail = common.parseDOM(li, "img", attrs = { "class": "[^\"']*playBroadcastThumbnail[^\"']*" }, ret = "src")[0]
      thumbnail = helper.prepareThumb(thumbnail)
      title = common.replaceHTMLCodes(title)
      article = {}
      article["title"] = title
      article["url"] = url
      article["thumbnail"] = thumbnail
      articles.append(article)
  
  return articles
  

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

def getSearchResults(url, listId):
  
  html = getPage(url)

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
    results.append({ "title" : title, "thumbnail" : thumbnail, "url" : url  })

  return results

def getAjaxUrl(html,tabname):
  """
  Fetches the Ajax URL from a program page.
  """
  common.log("tabname: " + tabname)

  container = getPlayBox(html,tabname) 

  attrs = { "class": CLASS_SHOW_MORE_BTN, "data-name": DATA_NAME_SHOW_MORE_BTN}
  
  ajaxurl = common.parseDOM(container,
                              "a",
                              attrs = attrs,
                              ret = "data-baseurl")
  if len(ajaxurl) > 0:
    return common.replaceHTMLCodes(ajaxurl[0])
  else:
    return None


def getLastPage(html,tabname):
  """
  Fetches the "data-lastpage" attribute from
  the "Visa fler" anchor.
  """
  container = getPlayBox(html,tabname)

  lastpage = common.parseDOM(container,
                 "a",
                 attrs = { "class": CLASS_SHOW_MORE_BTN, "data-name": DATA_NAME_SHOW_MORE_BTN},
                 ret = "data-lastpage")
  if len(lastpage) > 0:
    return lastpage[0]
  else: 
    return None


def getPlayBox(html,tabname):
  container = common.parseDOM(html,
                              "div",
                              attrs = { "class": "[^\"']*[playBoxBody|playBoxAltBody][^\"']*", "data-tabname": tabname })[0]
  return container


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
 
  for index,article in enumerate(articles):
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
