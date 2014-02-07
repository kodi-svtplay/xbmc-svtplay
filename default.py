# -*- coding: utf-8 -*-
import re
import json
import time
import urllib
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import CommonFunctions as common
import os
import resources.lib.bestofsvt as bestof
import resources.lib.helper as helper
import resources.lib.svt as svt

MODE_CHANNELS = "kanaler"
MODE_A_TO_O = "a-o"
MODE_PROGRAM = "pr"
MODE_CLIPS = "clips"
MODE_LIVE = "live"
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

pluginHandle = int(sys.argv[1])

addon = xbmcaddon.Addon()
localize = addon.getLocalizedString
xbmcplugin.setContent(pluginHandle, "tvshows")

common.plugin = addon.getAddonInfo('name') + ' ' + addon.getAddonInfo('version')

# Get and set settings
common.dbg = False
if addon.getSetting('debug') == "true":
  common.dbg = True

HLS_STRIP = False
if addon.getSetting("hlsstrip") == "true":
    HLS_STRIP = True

FULL_PROGRAM_PARSE = False
if addon.getSetting("fullparse") == "true":
  FULL_PROGRAM_PARSE = True

HIDE_SIGN_LANGUAGE = False
if addon.getSetting("hidesignlanguage") == "true":
  HIDE_SIGN_LANGUAGE = True 
SHOW_SUBTITLES = False
if addon.getSetting("showsubtitles") == "true":
  SHOW_SUBTITLES = True

USE_ALPHA_CATEGORIES = False
if addon.getSetting("alpha") == "true":
  USE_ALPHA_CATEGORIES = True

MAX_DIR_ITEMS = int(float(addon.getSetting("diritems")))

BW_SELECT = False
if addon.getSetting("bwselect") == "true":
  BW_SELECT = True

LOW_BANDWIDTH  = int(float(addon.getSetting("bandwidth")))
HIGH_BANDWIDTH = svt.getHighBw(LOW_BANDWIDTH)
LOW_BANDWIDH   = LOW_BANDWIDTH

def viewStart():

  addDirectoryItem(localize(30009), { "mode": MODE_POPULAR })
  addDirectoryItem(localize(30003), { "mode": MODE_LATEST, "page": 1 })
  addDirectoryItem(localize(30010), { "mode": MODE_LAST_CHANCE })
  addDirectoryItem(localize(30011), { "mode": MODE_LATEST_CLIPS })
  addDirectoryItem(localize(30000), { "mode": MODE_A_TO_O })
  addDirectoryItem(localize(30001), { "mode": MODE_CATEGORIES })
  addDirectoryItem(localize(30006), { "mode": MODE_SEARCH })


def viewAtoO():
  programs = svt.getAtoO()
  
  for program in programs:
    addDirectoryItem(program["title"], { "mode": MODE_PROGRAM, "url": program["url"], "page": 1 })


def viewCategories():
  categories = svt.getCategories()

  for category in categories:
    addDirectoryItem(category["title"], { "mode": MODE_CATEGORY, "url": category["url"] })


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
    addDirectoryItem(program["title"], { "mode" : MODE_PROGRAM, "url" : program["url"] }) 

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

  keyword = re.sub(r" ","+",keyword) 

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


def createDirItem(article,mode):
  """
  Given an article and a mode; create directory item
  for the article.
  """
  if (not HIDE_SIGN_LANGUAGE) or (article["title"].lower().endswith("teckentolkad") == False and article["title"].lower().find("teckenspråk".decode("utf-8")) == -1):

    params = {}
    params["mode"] = mode
    params["url"] = article["url"]
    folder = False

    if mode == MODE_PROGRAM:
      folder = True
      params["page"] = 1
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
  common.log("url: " + url)
  html = svt.getPage(url)

  jsonString = common.replaceHTMLCodes(html)
  jsonObj = json.loads(jsonString)
  common.log(jsonString)

  (videoUrl, errormsg) = getVideoUrl(jsonObj)
  subtitle = getSubtitle(jsonObj)
  player = xbmc.Player()
  startTime = time.time()

  if videoUrl:
    xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path=videoUrl))

    if subtitle:
      while not player.isPlaying() and time.time() - startTime < 10:
        time.sleep(1.)

      player.setSubtitles(subtitle)

      if not SHOW_SUBTITLES:
        player.showSubtitles(False)
  else:
    # No video URL was found
    dialog = xbmcgui.Dialog()
    if not errormsg:
      dialog.ok("SVT Play", localize(30100))
    else:
      dialog.ok("SVT Play", errormsg)


def getVideoUrl(jsonObj):
  """
  Returns a video URL from a JSON object and
  an error message, if available.
  """
  videoUrl = None
  extension = "None"
  args = ""

  for video in jsonObj["video"]["videoReferences"]:
    """
    Determine which file extension that will be used
    m3u8 is preferred, hence the break.
    Order: m3u8, f4m, mp4, flv
    """
    tmpurl = video["url"]
    argpos = tmpurl.rfind("?")
    errormsg = ""

    if argpos > 0:
      args = tmpurl[argpos:]
      tmpurl = tmpurl[:argpos]

    if tmpurl.endswith(".m3u8"):
      extension = "HLS"
      videoUrl = tmpurl
      break
    if tmpurl.endswith(".f4m"):
      extension = "F4M"
      videoUrl = tmpurl
      continue
    if tmpurl.endswith(".mp4"):
      extension = "MP4"
      videoUrl = tmpurl
      continue
    if tmpurl.endswith(".flv"):
      extension = "FLV"
      videoUrl = tmpurl
      continue
    videoUrl = tmpurl

  if extension == "HLS" and HLS_STRIP:
    videoUrl = hlsStrip(videoUrl)
  elif extension == "HLS" and BW_SELECT: 
    (videoUrl, errormsg) = getStreamForBW(videoUrl)

  if extension == "F4M":
    videoUrl = videoUrl.replace("/z/", "/i/").replace("manifest.f4m","master.m3u8")

  if extension == "MP4":
    videoUrl = mp4Handler(jsonObj)

  if extension == "None" and videoUrl:
    # No supported video was found
    common.log("No supported video extension found for URL: " + videoUrl)
    return None

  if args and not (HLS_STRIP or BW_SELECT):
    videoUrl = videoUrl + args

  if extension == "MP4" and videoUrl.startswith("rtmp://"):
    videoUrl = videoUrl + " swfUrl="+svt.SWF_URL+" swfVfy=1"

  return (videoUrl, errormsg)


def getSubtitle(jsonObj):
  """
  Returns a subtitle from a JSON object
  """
  subtitle = None

  for sub in jsonObj["video"]["subtitleReferences"]:
    if sub["url"].endswith(".wsrt"):
      subtitle = sub["url"]
    else:
      if len(sub["url"]) > 0:
        common.log("Skipping unknown subtitle: " + sub["url"])

  return subtitle


def mp4Handler(jsonObj):
  """
  Returns a mp4 stream URL.

  If there are several mp4 streams in the JSON object:
  pick the one with the highest bandwidth.

  Some programs are available with multiple mp4 streams
  for different bitrates. This function ensures that the one
  with the highest bitrate is chosen.

  Can possibly be extended to support some kind of quality
  setting in the plugin.
  """
  videos = []

  # Find all mp4 videos
  for video in jsonObj["video"]["videoReferences"]:
    if video["url"].endswith(".mp4"):
      videos.append(video)
  
  if len(videos) == 1:
    return videos[0]["url"]

  bitrate = 0
  url = ""

  # Find the video with the highest bitrate
  for video in videos:
    if video["bitrate"] > bitrate:
      bitrate = video["bitrate"]
      url = video["url"]          

  common.log("Info: bitrate="+str(bitrate)+" url="+url)
  return url


def hlsStrip(videoUrl):
    """
    Extracts the stream that supports the
    highest bandwidth and is not using the avc1.77.30 codec.
    Returns the path to a m3u8 file on the local disk with a
    reference to the extracted stream.
    """
    common.log("Stripping file: " + videoUrl)

    ufile = urllib.urlopen(videoUrl)
    lines = ufile.readlines()

    newplaylist = "#EXTM3U\n"
    hlsurl = ""
    bandwidth = 0
    foundhigherquality = False

    for line in lines:
      if foundhigherquality:
        # The stream url is on the line proceeding the header
        foundhigherquality = False
        hlsurl = line
      if "EXT-X-STREAM-INF" in line: # The header
        if not "avc1.77.30" in line:
          match = re.match(r'.*BANDWIDTH=(\d+).+',line)
          if match:
            if bandwidth < int(match.group(1)):
              foundhigherquality = True
              bandwidth = int(match.group(1))
          continue

    if bandwidth == 0:
      return None

    ufile.close()
    hlsurl = hlsurl.rstrip()
    common.log("Returned stream url : " + hlsurl)
    return hlsurl


def getStreamForBW(url):
  """
  Returns a stream URL for the set bandwidth,
  and an error message, if applicable.
  """
  
  f = urllib.urlopen(url)
  lines = f.readlines()
  
  hlsurl = ""
  marker = "#EXT-X-STREAM-INF"
  found = False

  for line in lines:
    if found:
      # The stream url is on the line proceeding the header
      hlsurl = line
      break
    if marker in line: # The header
      match = re.match(r'.*BANDWIDTH=(\d+)000.+',line)
      if match:
        if LOW_BANDWIDTH < int(match.group(1)) < HIGH_BANDWIDTH:
          common.log("Found stream with bandwidth " + match.group(1) + " for selected bandwidth " + str(LOW_BANDWIDTH))
          found = True
  
  f.close()

  if found:
    hlsurl = hlsurl.rstrip()
    common.log("Returned stream url: " + hlsurl)
    return (hlsurl, '')
  else:
    errormsg = "No stream found for bandwidth setting " + str(LOW_BANDWIDTH)
    common.log(errormsg)
    return (None, errormsg)


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

  xbmcplugin.addDirectoryItem(pluginHandle, sys.argv[0] + '?' + urllib.urlencode(params), li, folder)


params = helper.getUrlParameters(sys.argv[2])

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
  if USE_ALPHA_CATEGORIES:
    viewAlphaDirectories()
  else:
    viewAtoO()
elif mode == MODE_CATEGORIES:
  viewCategories()
elif mode == MODE_CATEGORY:
  viewCategory(url)
elif mode == MODE_PROGRAM:
  viewEpisodes(url)
  addClipDirItem(url)
elif mode == MODE_CLIPS:
  viewClips(url)
elif mode == MODE_VIDEO:
  startVideo(url)
elif mode == MODE_LATEST:
  viewLatestVideos()
elif mode == MODE_POPULAR:
  viewPopular()
elif mode == MODE_LAST_CHANCE:
  viewLastChance()
elif mode == MODE_LATEST_CLIPS:
  viewLatestClips()
elif mode == MODE_LETTER:
  viewProgramsByLetter(letter)
elif mode == MODE_SEARCH:
  viewSearch()
elif mode == MODE_BESTOF_CATEGORIES:
  viewBestOfCategories()
elif mode == MODE_BESTOF_CATEGORY:
  viewBestOfCategory(url)

xbmcplugin.endOfDirectory(pluginHandle)
