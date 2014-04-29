# -*- coding: utf-8 -*-
import re
import json
import sys
import time
import urllib
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import CommonFunctions as common
import resources.lib.bestofsvt as bestof
import resources.lib.helper as helper
import resources.lib.svt as svt

MODE_CHANNELS = "kanaler"
MODE_A_TO_O = "a-o"
MODE_PROGRAM = "pr"
MODE_CLIPS = "clips"
MODE_LIVE_CHANNELS = "live-channels"
MODE_LATEST = "ep"
MODE_LATEST_NEWS = "en"
MODE_POPULAR = "popular"
MODE_LAST_CHANCE = "last-chance"
MODE_LATEST_CLIPS = "latest-clips"
MODE_VIDEO = "video"
MODE_CATEGORIES = "categories"
MODE_CATEGORY = "ti"
MODE_LETTER = "letter"
MODE_RECOMMENDED = "rp"
MODE_SEARCH = "search"
MODE_BESTOF_CATEGORIES = "bestofcategories"
MODE_BESTOF_CATEGORY = "bestofcategory"
MODE_VIEW_TITLES = "view_titles"
MODE_VIEW_EPISODES = "view_episodes"
MODE_VIEW_CLIPS = "view_clips"

S_DEBUG = "debug"
S_HIDE_SIGN_LANGUAGE = "hidesignlanguage"
S_SHOW_SUBTITLES = "showsubtitles"
S_USE_ALPHA_CATEGORIES = "alpha"
S_BW_SELECT = "bwselect"
S_HLS_STRIP = "hlsstrip"

PLUGIN_HANDLE = int(sys.argv[1])

addon = xbmcaddon.Addon("plugin.video.svtplay")
localize = addon.getLocalizedString
xbmcplugin.setContent(PLUGIN_HANDLE, "tvshows")

common.plugin = addon.getAddonInfo('name') + ' ' + addon.getAddonInfo('version')
common.dbg = helper.getSetting(S_DEBUG)


def viewStart():

  addDirectoryItem(localize(30009), { "mode": MODE_POPULAR })
  addDirectoryItem(localize(30003), { "mode": MODE_LATEST })
  addDirectoryItem(localize(30010), { "mode": MODE_LAST_CHANCE })
  addDirectoryItem(localize(30002), { "mode": MODE_LIVE_CHANNELS })
  addDirectoryItem(localize(30000), { "mode": MODE_A_TO_O })
  addDirectoryItem(localize(30001), { "mode": MODE_CATEGORIES })
  addDirectoryItem(localize(30007), { "mode": MODE_BESTOF_CATEGORIES })
  addDirectoryItem(localize(30006), { "mode": MODE_SEARCH })


def viewAtoO():
  programs = svt.getAtoO()
  
  for program in programs:
    addDirectoryItem(program["title"], { "mode": MODE_PROGRAM, "url": program["url"] })


def viewCategories():
  categories = svt.getCategories()

  for category in categories:
    addDirectoryItem(category["title"], { "mode": MODE_CATEGORY, "url": category["url"] }, thumbnail=category["thumbnail"])


def viewAlphaDirectories():
  alphas = svt.getAlphas() 
  if not alphas:
    return
  for alpha in alphas:
    addDirectoryItem(alpha["title"], { "mode": MODE_LETTER, "letter": alpha["char"] })


def viewProgramsByLetter(letter):
  programs = svt.getProgramsByLetter(letter)

  for program in programs:
    addDirectoryItem(program["title"], { "mode": MODE_PROGRAM, "url": program["url"] })

def viewPopular():
  articles = svt.getArticles(svt.SECTION_POPULAR)
  if not articles:
    return
  for article in articles:
    createDirItem(article, MODE_VIDEO)

def viewLatestVideos():
  articles = svt.getArticles(svt.SECTION_LATEST_VIDEOS)
  if not articles:
    return
  for article in articles:
    createDirItem(article, MODE_VIDEO)

def viewLastChance():
  articles = svt.getArticles(svt.SECTION_LAST_CHANCE)
  if not articles:
    return
  for article in articles:
    createDirItem(article, MODE_VIDEO)

def viewLatestClips():
  articles = svt.getArticles(svt.SECTION_LATEST_CLIPS)
  if not articles:
    return
  for article in articles:
    createDirItem(article, MODE_VIDEO)

def viewLiveChannels():
  articles = svt.getArticles(svt.SECTION_LIVE_CHANNELS)
  if not articles:
    return
  for article in articles:
    createDirItem(article, MODE_VIDEO)

def viewCategory(url):
  if url == svt.URL_TO_OA:
    dialog = xbmcgui.Dialog()
    dialog.ok("SVT Play", localize(30107))
    viewStart()
    return 

  programs = svt.getProgramsForCategory(url)
  if not programs:
    return
  for program in programs:
    addDirectoryItem(program["title"], { "mode" : MODE_PROGRAM, "url" : program["url"] }, thumbnail=program["thumbnail"]) 

def viewEpisodes(url):
  """
  Displays the episodes for a program with URL 'url'.
  """
  episodes = svt.getArticles(svt.SECTION_EPISODES, url)
  if not episodes:
    common.log("No episodes found!")
    return
  
  for episode in episodes:
    createDirItem(episode, MODE_VIDEO)

def addClipDirItem(url):
  """
  Adds the "Clips" directory item to a program listing.
  """
  params = {}
  params["mode"] = MODE_CLIPS
  params["url"] = url
  addDirectoryItem(localize(30108), params)

def viewClips(url):
  """
  Displays the latest clips for a program
  """
  clips = svt.getArticles(svt.SECTION_LATEST_CLIPS, url)
  if not clips:
    common.log("No clips found!")
    return
  
  for clip in clips:
    createDirItem(clip, MODE_VIDEO)

def viewSearch():

  keyword = common.getUserInput(localize(30102))
  if keyword == "" or not keyword:
    viewStart()
    return
  keyword = urllib.quote(keyword)
  common.log("Search string: " + keyword)

  keyword = re.sub(r" ", "+", keyword) 

  url = svt.URL_TO_SEARCH + keyword
 
  results = svt.getSearchResults(url)
  for result in results:
    mode = MODE_VIDEO
    if result["type"] == "program":
      mode = MODE_PROGRAM
    createDirItem(result["item"], mode)


def viewBestOfCategories():
  """
  Creates a directory displaying each of the
  categories from the bestofsvt page
  """
  categories = bestof.getCategories()
  params = {}
  params["mode"] = MODE_BESTOF_CATEGORY

  for category in categories:
    params["url"] = category["url"]
    addDirectoryItem(category["title"], params)


def viewBestOfCategory(url):
  """
  Creates a directory containing all shows displayed
  for a category
  """
  shows = bestof.getShows(url)
  params = {}
  params["mode"] = MODE_VIDEO

  for show in shows:
    params["url"] = show["url"]
    addDirectoryItem(show["title"], params, show["thumbnail"], False, False, show["info"])


def createDirItem(article, mode):
  """
  Given an article and a mode; create directory item
  for the article.
  """
  if not helper.getSetting(S_HIDE_SIGN_LANGUAGE) or (article["title"].lower().endswith("teckentolkad") == False and article["title"].lower().find("teckenspråk".decode("utf-8")) == -1):

    params = {}
    params["mode"] = mode
    params["url"] = article["url"]
    folder = False

    if mode == MODE_PROGRAM:
      folder = True
    info = None
    if "info" in article.keys():
      info = article["info"]
    addDirectoryItem(article["title"], params, article["thumbnail"], folder, False, info)


def startVideo(url):
  """
  Starts the XBMC player if a valid video URL is 
  found for the given page URL.
  """
  if not url.startswith("/"):
    url = "/" + url

  url = url + svt.JSON_SUFFIX
  html = svt.getPage(url)

  json_string = common.replaceHTMLCodes(html)
  json_obj = json.loads(json_string)
  common.log(json_string)

  video_url = helper.getVideoUrl(json_obj)
  errormsg = None
  extension = helper.getVideoExtension(video_url)

  if not extension and video_url:
    # No supported video was found
    common.log("No supported video extension found for URL: " + video_url)
    return None

  if extension == "HLS":
    if helper.getSetting(S_HLS_STRIP):
      video_url = helper.hlsStrip(video_url)
    elif helper.getSetting(S_BW_SELECT): 
      (video_url, errormsg) = helper.getStreamForBW(video_url)
  
  # MP4 support is disabled until it shows up on SVT Play again
  # since it today unclear how the mp4 streams will be served.
  #if extension == "MP4":
  #  video_url = helper.mp4Handler(json_obj)
  #  if video_url.startswith("rtmp://"):
  #    video_url = video_url + " swfUrl="+svt.SWF_URL+" swfVfy=1"

  subtitle_url = helper.getSubtitleUrl(json_obj)
  player = xbmc.Player()
  startTime = time.time()

  if video_url:
    xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, True, xbmcgui.ListItem(path=video_url))

    if subtitle_url:
      while not player.isPlaying() and time.time() - startTime < 10:
        time.sleep(1.)

      player.setSubtitles(subtitle_url)

      if not helper.getSetting(S_SHOW_SUBTITLES):
        player.showSubtitles(False)
  else:
    # No video URL was found
    dialog = xbmcgui.Dialog()
    if not errormsg:
      dialog.ok("SVT Play", localize(30100))
    else:
      dialog.ok("SVT Play", errormsg)


def addDirectoryItem(title, params, thumbnail = None, folder = True, live = False, info = None):

  li = xbmcgui.ListItem(title)

  if thumbnail:
    li.setThumbnailImage(thumbnail)

  if live:
    li.setProperty("IsLive", "true")

  if not folder:
    li.setProperty("IsPlayable", "true")

  if info:
    li.setInfo("Video", info)

  xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, sys.argv[0] + '?' + urllib.urlencode(params), li, folder)

# Main segment of script
ARG_PARAMS = helper.getUrlParameters(sys.argv[2])
ARG_MODE = ARG_PARAMS.get("mode")
ARG_URL = urllib.unquote_plus(ARG_PARAMS.get("url", ""))

if not ARG_MODE:
  viewStart()
elif ARG_MODE == MODE_A_TO_O:
  if helper.getSetting(S_USE_ALPHA_CATEGORIES):
    viewAlphaDirectories()
  else:
    viewAtoO()
elif ARG_MODE == MODE_CATEGORIES:
  viewCategories()
elif ARG_MODE == MODE_CATEGORY:
  viewCategory(ARG_URL)
elif ARG_MODE == MODE_PROGRAM:
  viewEpisodes(ARG_URL)
  addClipDirItem(ARG_URL)
elif ARG_MODE == MODE_CLIPS:
  viewClips(ARG_URL)
elif ARG_MODE == MODE_VIDEO:
  startVideo(ARG_URL)
elif ARG_MODE == MODE_LATEST:
  viewLatestVideos()
elif ARG_MODE == MODE_POPULAR:
  viewPopular()
elif ARG_MODE == MODE_LAST_CHANCE:
  viewLastChance()
elif ARG_MODE == MODE_LIVE_CHANNELS:
  viewLiveChannels()
elif ARG_MODE == MODE_LATEST_CLIPS:
  viewLatestClips()
elif ARG_MODE == MODE_LETTER:
  viewProgramsByLetter(ARG_PARAMS.get("letter"))
elif ARG_MODE == MODE_SEARCH:
  viewSearch()
elif ARG_MODE == MODE_BESTOF_CATEGORIES:
  viewBestOfCategories()
elif ARG_MODE == MODE_BESTOF_CATEGORY:
  viewBestOfCategory(ARG_URL)

xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
