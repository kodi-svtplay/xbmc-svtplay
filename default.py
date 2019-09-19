# -*- coding: utf-8 -*-
# system imports
from __future__ import absolute_import,unicode_literals
import re
import os
import sys
import time
import urllib
import xbmc # pylint: disable=import-error
import xbmcgui # pylint: disable=import-error
import xbmcaddon # pylint: disable=import-error
import xbmcplugin # pylint: disable=import-error
# own imports
from resources.lib import helper
from resources.lib import svt
from resources.lib import logging
from resources.lib.mode.common import Common

try:
  # Python 2
  from urllib import quote, urlencode, unquote_plus
except ImportError:
  # Python 3
  from urllib.parse import quote, urlencode, unquote_plus

MODE_CHANNELS = "kanaler"
MODE_A_TO_O = "a-o"
MODE_PROGRAM = "pr"
MODE_CLIPS = "clips"
MODE_LIVE_PROGRAMS = "live"
MODE_LATEST = "latest"
MODE_LATEST_NEWS = 'news'
MODE_POPULAR = "popular"
MODE_LAST_CHANCE = "last_chance"
MODE_VIDEO = "video"
MODE_CATEGORIES = "categories"
MODE_CATEGORY = "ti"
MODE_LETTER = "letter"
MODE_SEARCH = "search"
MODE_VIEW_TITLES = "view_titles"
MODE_VIEW_EPISODES = "view_episodes"
MODE_VIEW_CLIPS = "view_clips"

# settings keys
S_SHOW_SUBTITLES = "showsubtitles"
S_USE_ALPHA_CATEGORIES = "alpha"

# plugin setup
PLUGIN_HANDLE = int(sys.argv[1])
addon = xbmcaddon.Addon("plugin.video.svtplay")
localize = addon.getLocalizedString
xbmcplugin.setContent(PLUGIN_HANDLE, "tvshows")
xbmcplugin.addSortMethod(PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_LABEL)

DEFAULT_FANART = os.path.join(
  xbmc.translatePath(addon.getAddonInfo("path") + "/resources/images/"),
  "background.png")

common = Common(addon, sys.argv[0], PLUGIN_HANDLE, DEFAULT_FANART) 

def view_start():
  common.add_directory_item(localize(30009), {"mode": MODE_POPULAR})
  common.add_directory_item(localize(30003), {"mode": MODE_LATEST})
  common.add_directory_item(localize(30004), {"mode": MODE_LATEST_NEWS})
  common.add_directory_item(localize(30010), {"mode": MODE_LAST_CHANCE})
  common.add_directory_item(localize(30002), {"mode": MODE_LIVE_PROGRAMS})
  common.add_directory_item(localize(30008), {"mode": MODE_CHANNELS})
  common.add_directory_item(localize(30000), {"mode": MODE_A_TO_O})
  common.add_directory_item(localize(30001), {"mode": MODE_CATEGORIES})
  common.add_directory_item(localize(30006), {"mode": MODE_SEARCH})

def view_a_to_z():
  programs = svt.getAtoO()
  __program_listing(programs)

def view_alpha_directories():
  letters = svt.getAlphas()
  if not letters:
    return
  for letter in letters:
    common.add_directory_item(letter, {"mode": MODE_LETTER, "letter": letter.encode("utf-8")})

def view_programs_by_letter(letter):
  programs = svt.getProgramsByLetter(letter)
  __program_listing(programs)

def __program_listing(programs):
  for program in programs:
    if common.is_geo_restricted(program):
      logging.log("Not showing {} as it is restricted to Sweden and geo setting is on".format(program["title"]))
      continue
    folder = True
    mode = common.MODE_PROGRAM
    if program["type"] == "video":
      mode = common.MODE_VIDEO
      folder = False
    common.add_directory_item(program["title"],
                {"mode": mode, "url": program["url"]},
                thumbnail=program["thumbnail"], folder=folder)

def view_categories():
  categories = svt.getCategories()
  for category in categories:
    common.add_directory_item(category["title"],
                {"mode": MODE_CATEGORY, "url": category["genre"]})

def view_section(section, page):
  (items, more_items) = svt.getItems(section, page)
  if not items:
    return
  for item in items:
    mode = common.MODE_VIDEO
    if item["type"] == "program":
      mode = common.MODE_PROGRAM
    common.create_dir_item(item, mode)
  if more_items:
    common.add_next_page_item(page+1, section)

def view_channels():
  channels = svt.getChannels()
  if not channels:
    return
  for channel in channels:
    common.create_dir_item(channel, MODE_VIDEO)

def view_latest_news():
    items = svt.getLatestNews()
    if not items:
      return
    for item in items:
      common.create_dir_item(item, MODE_VIDEO)

def view_category(genre):
  programs = svt.getProgramsForGenre(genre)
  if not programs:
    return
  for program in programs:
    mode = MODE_PROGRAM
    if program["type"] == "video":
      mode = MODE_VIDEO
    common.create_dir_item(program, mode)

def view_episodes(url):
  """
  Displays the episodes for a program
  """
  logging.log("View episodes for {}".format(url))
  episodes = svt.getEpisodes(url.split("/")[-1])
  if episodes is None:
    logging.log("No episodes found")
    return
  for episode in episodes:
    common.create_dir_item(episode, MODE_VIDEO)

def __add_clip_dir_item(url):
  """
  Adds the "Clips" directory item to a program listing.
  """
  params = {}
  params["mode"] = MODE_CLIPS
  params["url"] = url
  common.add_directory_item(localize(30108), params)

def view_clips(url):
  """
  Displays the latest clips for a program
  """
  logging.log("View clips for {}".format(url))
  clips = svt.getClips(url.split("/")[-1])
  if not clips:
    logging.log("No clips found")
    return
  for clip in clips:
    common.create_dir_item(clip, MODE_VIDEO)

def view_search():
  keyword = helper.getInputFromKeyboard(localize(30102))
  if keyword == "" or not keyword:
    view_start()
    return
  keyword = quote(keyword)
  logging.log("Search string: " + keyword)
  keyword = re.sub(r" ", "+", keyword)
  keyword = keyword.strip()
  results = svt.getSearchResults(keyword)
  for result in results:
    mode = MODE_VIDEO
    if result["type"] == "program":
      mode = MODE_PROGRAM
    common.create_dir_item(result["item"], mode)

def start_video(video_id):
  video_json = svt.getVideoJSON(video_id)
  if video_json is None:
    logging.log("ERROR: Could not get video JSON")
    return
  try:
    show_obj = helper.resolveShowJSON(video_json)
  except ValueError:
    logging.log("Could not decode JSON for "+video_id)
    return
  if show_obj["videoUrl"]:
    play_video(show_obj)
  else:
    dialog = xbmcgui.Dialog()
    dialog.ok("SVT Play", localize(30100))

def play_video(show_obj):
  player = xbmc.Player()
  start_time = time.time()
  xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, True, xbmcgui.ListItem(path=show_obj["videoUrl"]))
  if show_obj["subtitleUrl"]:
    while not player.isPlaying() and time.time() - start_time < 10:
      time.sleep(1.)
    player.setSubtitles(show_obj["subtitleUrl"])
    if not helper.getSetting(S_SHOW_SUBTITLES):
      player.showSubtitles(False)

# Main segment of script
ARG_PARAMS = helper.getUrlParameters(sys.argv[2])
logging.log("params: {}".format(ARG_PARAMS))
ARG_MODE = ARG_PARAMS.get("mode")
ARG_URL = unquote_plus(ARG_PARAMS.get("url", ""))
ARG_PAGE = ARG_PARAMS.get("page")
if not ARG_PAGE:
  ARG_PAGE = "1"

if not ARG_MODE:
  view_start()
elif ARG_MODE == MODE_A_TO_O:
  if helper.getSetting(S_USE_ALPHA_CATEGORIES):
    view_alpha_directories()
  else:
    view_a_to_z()
elif ARG_MODE == MODE_CATEGORIES:
  view_categories()
elif ARG_MODE == MODE_CATEGORY:
  view_category(ARG_URL)
elif ARG_MODE == MODE_PROGRAM:
  view_episodes(ARG_URL)
  __add_clip_dir_item(ARG_URL)
elif ARG_MODE == MODE_CLIPS:
  view_clips(ARG_URL)
elif ARG_MODE == MODE_VIDEO:
  start_video(ARG_URL)
elif ARG_MODE == MODE_POPULAR or \
     ARG_MODE == MODE_LATEST or \
     ARG_MODE == MODE_LAST_CHANCE or \
     ARG_MODE == MODE_LIVE_PROGRAMS:
  view_section(ARG_MODE, int(ARG_PAGE))
elif ARG_MODE == MODE_LATEST_NEWS:
  view_latest_news()
elif ARG_MODE == MODE_CHANNELS:
  view_channels()
elif ARG_MODE == MODE_LETTER:
  view_programs_by_letter(ARG_PARAMS.get("letter"))
elif ARG_MODE == MODE_SEARCH:
  view_search()

xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
