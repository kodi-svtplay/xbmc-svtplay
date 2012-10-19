# -*- coding: utf-8 -*-
import re
import json
import time
import urllib
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import CommonFunctions

MODE_A_TO_O = "a-o"
MODE_PROGRAM = "pr"
MODE_LIVE = "live"
MODE_LATEST = "ep"
MODE_LATEST_NEWS = "en"
MODE_VIDEO = "video"
MODE_CATEGORIES = "categories"
MODE_CATEGORY = "ti"
MODE_LETTER = "letter"
MODE_RECOMMENDED = "rp"

BASE_URL = "http://www.svtplay.se"

URL_A_TO_O = "/program"
URL_CATEGORIES = "/kategorier"
URL_TO_LATEST = "?ep=1"
URL_TO_LATEST_NEWS = "?en=1"
URL_TO_RECOMMENDED = "?rp=1"

VIDEO_PATH_RE = "/(klipp|video|live)/\d+"
VIDEO_PATH_SUFFIX = "?type=embed"

MAX_NUM_GRID_ITEMS = 12
CURR_DIR_ITEMS = 0

pluginHandle = int(sys.argv[1])

settings = xbmcaddon.Addon()
localize = settings.getLocalizedString

common = CommonFunctions
common.plugin = "SVT Play 3"

if settings.getSetting('debug') == "true":
  common.dbg = True
else:
  common.dbg = False

MAX_DIR_ITEMS = int(float(settings.getSetting("diritems")))

def viewStart():

  addDirectoryItem(localize(30000), { "mode": MODE_A_TO_O })
  addDirectoryItem(localize(30001), { "mode": MODE_CATEGORIES })
  addDirectoryItem(localize(30005), { "mode": MODE_RECOMMENDED, "page": 1 })
  addDirectoryItem(localize(30002), { "mode": MODE_LIVE })
  addDirectoryItem(localize(30003), { "mode": MODE_LATEST, "page": 1 })
  addDirectoryItem(localize(30004), { "mode": MODE_LATEST_NEWS, "page": 1 })

def viewAtoO():
  html = getPage(BASE_URL + URL_A_TO_O)

  texts = common.parseDOM(html, "a" , attrs = { "class": "playLetterLink" })
  hrefs = common.parseDOM(html, "a" , attrs = { "class": "playLetterLink" }, ret = "href")

  for index, text in enumerate(texts):
    addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_PROGRAM, "url": hrefs[index], "page": 1 })

def viewLive():
  html = getPage(BASE_URL)

  tabId = common.parseDOM(html, "a", attrs = { "class": "[^\"']*playButton-TabLive[^\"']*" }, ret = "data-tab")

  if len(tabId) > 0:

    tabId = tabId[0]

    container = common.parseDOM(html, "div", attrs = { "class": "[^\"']*svtTab-" + tabId + "[^\"']*" })

    lis = common.parseDOM(container, "li", attrs = { "class": "[^\"']*svtMediaBlock[^\"']*" })

    for li in lis:

      liveIcon = common.parseDOM(li, "img", attrs = { "class": "[^\"']*playBroadcastLiveIcon[^\"']*"})

      if len(liveIcon) > 0:

        text = common.parseDOM(li, "h5")[0]
        href = common.parseDOM(li, "a", ret = "href")[0]

        match = re.match(VIDEO_PATH_RE, href)

        if match:

          url = match.group() + VIDEO_PATH_SUFFIX

          addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_VIDEO, "url": url }, None, False, True)

def viewCategories():
  html = getPage(BASE_URL + URL_CATEGORIES)

  container = common.parseDOM(html, "ul", attrs = { "class": "[^\"']*svtGridBlock[^\"']*" })

  lis = common.parseDOM(container, "li" , attrs = { "class": "[^\"']*svtMediaBlock[^\"']*" })

  for li in lis:

    href = common.parseDOM(li, "a", ret = "href")[0]
    text = common.parseDOM(li, "h2")[0]

    addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_CATEGORY, "url": href, "page": 1})

def viewAlphaDirectories():
  """
  Used to create the alphabetical A-Ö directory items.
  Addon setting has to be enabled for this to trigger.
  """
  html = getPage(BASE_URL + URL_A_TO_O)

  container = common.parseDOM(html, "ul", attrs = { "id" : "playLetterList" })

  letters = common.parseDOM(container, "h2", attrs = { "class" : "playLetterHeading " })

  for letter in letters:
    url = letter
    addDirectoryItem(convertChar(letter), { "mode": MODE_LETTER, "letter": url })

def viewProgramsByLetter(letter):

  letter = urllib.unquote(letter)

  html = getPage(BASE_URL + URL_A_TO_O)

  container = common.parseDOM(html, "ul", attrs = { "id": "playLetterList" })

  letterboxes = common.parseDOM(container, "div", attrs = { "class": "playLetter" })

  for letterbox in letterboxes:

    heading = common.parseDOM(letterbox, "h2")[0]

    if heading == letter:
      break

  lis = common.parseDOM(letterbox, "li", attrs = { "class": "playListItem" })

  for li in lis:

    href = common.parseDOM(li, "a", ret = "href")[0]
    text = common.parseDOM(li, "a")[0]

    addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_PROGRAM, "url": href, "page": 1 })


def viewLatest(mode,page,index):

  dirtype = MODE_VIDEO

  if mode == MODE_LATEST_NEWS:
    url = URL_TO_LATEST_NEWS
  elif mode == MODE_RECOMMENDED:
    url = URL_TO_RECOMMENDED
    dirtype = MODE_PROGRAM
  elif mode == MODE_LATEST:
    url = URL_TO_LATEST

  createDirectory(url,page,index,mode,dirtype)


def viewCategory(url,page,index):

  createDirectory(url,page,index,MODE_CATEGORY,MODE_PROGRAM)


def viewProgram(url,page,index):

  createDirectory(url,page,index,MODE_PROGRAM,MODE_VIDEO)


def createDirectory(url,page,index,callertype,dirtype):
  """
  Parses Ajax URL and last page number from the argument url and
  then calls populateDir to populate a directory with
  video/program items.
  """
  if not url.startswith("/"):
    url = "/" + url

  html = getPage(BASE_URL + url)
  ajaxurl = common.parseDOM(html,
                "ul",
                attrs = { "class": "playLargePager", "data-name": callertype },
                ret = "data-baseurl")[0]
  lastpage = common.parseDOM(html,
                 "ul",
                 attrs = { "class": "playLargePager", "data-name": callertype },
                 ret = "data-lastpage")[0]

  fetchitems = True
  pastlastpage = False

  ajaxurl = common.replaceHTMLCodes(ajaxurl)
  page = int(page)
  index = int(index)
  lastpage = int(lastpage)

  while fetchitems:

    if page > lastpage:
      pastlastpage = True
      break

    (fetchitems,lastindex) = populateDir(ajaxurl,dirtype,str(page),index)
    page += 1

  if not pastlastpage:
    page = page - 1
    addDirectoryItem(localize(30101),
             { "mode": callertype,
               "url": url,
               "page": str(page),
               "index": lastindex})


def populateDir(ajaxurl,mode,page,index):
  """
  Populates a directory with items from a "Ajax" page.

  index is used as a starting reference if the not
  all items on a page were used to populate the previous
  directory.
  """
  global CURR_DIR_ITEMS

  html = getPage(BASE_URL + ajaxurl + "page=" + page)
  container = common.parseDOM(html,
                "div",
                attrs = { "class": "[^\"']*svtGridBlock[^\"']*" })[0]
  articles = common.parseDOM(container, "article")

  articles = articles[index:]
  index = 0

  for article in articles:

    if CURR_DIR_ITEMS >= MAX_DIR_ITEMS:
      CURR_DIR_ITEMS = 0
      return (False,index)

    text = common.parseDOM(article, "h5")[0]
    href = common.parseDOM(article, "a", ret = "href")[0]
    thumbnail = common.parseDOM(article,
                  "img",
                  attrs = { "class": "playGridThumbnail" },
                  ret = "src")[0]
    thumbnail = thumbnail.replace("/small/", "/large/")

    if mode == MODE_VIDEO:
      href = href + VIDEO_PATH_SUFFIX
      addDirectoryItem(common.replaceHTMLCodes(text),
               { "mode": mode, "url": href }, thumbnail, False)
    elif mode == MODE_PROGRAM:
      addDirectoryItem(common.replaceHTMLCodes(text),
               { "mode": mode, "url": href, "page": 1 }, thumbnail)

    CURR_DIR_ITEMS += 1
    index += 1

  return (True,0)

def startVideo(url):

  if not url.startswith("/"):
    url = "/" + url

  html = getPage(BASE_URL + url)

  jsonString = common.parseDOM(html, "param", attrs = { "name": "flashvars" }, ret = "value")[0]

  jsonString = jsonString.lstrip("json=")
  jsonString = common.replaceHTMLCodes(jsonString)

  jsonObj = json.loads(jsonString)

  common.log(jsonString)

  subtitle = None
  player = xbmc.Player()
  startTime = time.time()
  videoUrl = None

  for video in jsonObj["video"]["videoReferences"]:
    if video["url"].find(".m3u8") > 0:
      videoUrl = video["url"]
      break
    if video["url"].endswith(".flv"):
      videoUrl = video["url"]
      break
    else:
      if video["url"].endswith("/manifest.f4m"):
        videoUrl = video["url"].replace("/z/", "/i/").replace("/manifest.f4m", "/master.m3u8")
      else:
        common.log("Skipping unknown filetype: " + video["url"])

  for sub in jsonObj["video"]["subtitleReferences"]:
    if sub["url"].endswith(".wsrt"):
      subtitle = sub["url"]
    else:
      if len(sub["url"]) > 0:
        common.log("Skipping unknown subtitle: " + sub["url"])

  if videoUrl:

    xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path=videoUrl))

    if subtitle:

      while not player.isPlaying() and time.time() - startTime < 10:
        time.sleep(1.)

      player.setSubtitles(subtitle)

      if settings.getSetting("showsubtitles") == "false":
        player.showSubtitles(False)
  else:
    dialog = xbmcgui.Dialog()
    dialog.ok("SVT PLAY", localize(30100))

def getPage(url):

  result = common.fetchPage({ "link": url })

  if result["status"] == 200:
    	return result["content"]

  if result["status"] == 500:
    common.log("redirect url: %s" %result["new_url"])
    common.log("header: %s" %result["header"])
    common.log("content: %s" %result["content"])


def addDirectoryItem(title, params, thumbnail = None, folder = True, live = False):

  li = xbmcgui.ListItem(title)

  if thumbnail:
    li.setThumbnailImage(thumbnail)

  if live:
    li.setProperty("IsLive", "true")

  if not folder:
    li.setProperty("IsPlayable", "true")

  xbmcplugin.addDirectoryItem(pluginHandle, sys.argv[0] + '?' + urllib.urlencode(params), li, folder)


def convertChar(char):
  if char == "&Aring;":
    return "Å"
  elif char == "&Auml;":
    return "Ä"
  elif char == "&Ouml;":
    return "Ö"
  else:
    return char

params = common.getParameters(sys.argv[2])

mode = params.get("mode")
url = urllib.unquote_plus(params.get("url", ""))
page = params.get("page")
letter = params.get("letter")
index = params.get("index")

if not index:
  index = "0"

if not mode:
  viewStart()
elif mode == MODE_A_TO_O:
  if settings.getSetting("alpha") == "true":
    viewAlphaDirectories()
  else:
    viewAtoO()
elif mode == MODE_LIVE:
  viewLive()
elif mode == MODE_CATEGORIES:
  viewCategories()
elif mode == MODE_CATEGORY:
  viewCategory(url,page,index)
elif mode == MODE_PROGRAM:
  viewProgram(url,page,index)
elif mode == MODE_VIDEO:
  startVideo(url)
elif mode == MODE_LATEST:
  viewLatest(mode,page,index)
elif mode == MODE_LATEST_NEWS:
  viewLatest(mode,page,index)
elif mode == MODE_LETTER:
  viewProgramsByLetter(letter)
elif mode == MODE_RECOMMENDED:
  viewLatest(mode,page,index)

xbmcplugin.endOfDirectory(pluginHandle)
