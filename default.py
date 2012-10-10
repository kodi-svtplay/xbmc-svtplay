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
MODE_PROGRAM = "program"
MODE_LIVE = "live"
MODE_VIDEO = "video"
MODE_CATEGORIES = "categories"
MODE_CATEGORY = "category"

BASE_URL = "http://www.svtplay.se"

URL_A_TO_O = "/program"
URL_CATEGORIES = "/kategorier"

VIDEO_PATH_RE = "/(klipp|video|live)/\d+"
VIDEO_PATH_SUFFIX = "?type=embed"

pluginHandle = int(sys.argv[1])

settings = xbmcaddon.Addon()
localize = settings.getLocalizedString

common = CommonFunctions
common.plugin = "SVT Play 3"

if settings.getSetting('debug') == "true":
	common.dbg = True
else:
	common.dbg = False

def viewStart():
	
	addDirectoryItem(localize(30000), { "mode": MODE_A_TO_O })
	addDirectoryItem(localize(30001), { "mode": MODE_CATEGORIES })
	addDirectoryItem(localize(30002), { "mode": MODE_LIVE })

def viewAtoO():
	html = getPage(BASE_URL + URL_A_TO_O)

	texts = common.parseDOM(html, "a" , attrs = { "class": "playLetterLink" })
	hrefs = common.parseDOM(html, "a" , attrs = { "class": "playLetterLink" }, ret = "href")

	for index, text in enumerate(texts):
		addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_PROGRAM, "url": hrefs[index] })

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

		addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_CATEGORY, "url": href })

def viewCategory(url):
	
	if not url.startswith("/"):
		url = "/" + url

	html = getPage(BASE_URL + url)

	container = common.parseDOM(html, "div", attrs = { "class": "[^\"']*playPagerSections[^\"']*" })[0]

	articles = common.parseDOM(container, "article")

	# TODO: Add paging
	for article in articles:
	
		href = common.parseDOM(article, "a", ret = "href")[0]
		text = common.parseDOM(article, "h5")[0]

		addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_PROGRAM, "url": href })

def viewProgram(url):
	
	if not url.startswith("/"):
		url = "/" + url
	
	html = getPage(BASE_URL + url)

	container = common.parseDOM(html, "div", attrs = { "class": "[^\"']*playPagerSections[^\"']*" })[0]

	articles = common.parseDOM(container, "article")

	# TODO: Add paging
	for article in articles:
		href = common.parseDOM(article, "a", ret = "href")[0]
		text = common.parseDOM(article, "h5")[0]
		thumbnail = common.parseDOM(article, "img", attrs = { "class": "playGridThumbnail" }, ret = "src")[0]
		
		# Get a larger image
		thumbnail = thumbnail.replace("/small/", "/large/")

		match = re.match(VIDEO_PATH_RE, href)
	
		if match:
		
			url = match.group() + VIDEO_PATH_SUFFIX
					
			addDirectoryItem(common.replaceHTMLCodes(text), { "mode": MODE_VIDEO, "url": url }, thumbnail, False)

def startVideo(url):
	
	if not url.startswith("/"):
		url = "/" + url
	
	html = getPage(BASE_URL + url)

	jsonString = common.parseDOM(html, "param" , attrs = { "name": "flashvars" }, ret = "value")[0]
	
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

params = common.getParameters(sys.argv[2])

mode = params.get("mode")
url = urllib.unquote_plus(params.get("url", ""))

if not mode:
	viewStart()
elif mode == MODE_A_TO_O:
	viewAtoO()
elif mode == MODE_LIVE:
	viewLive()
elif mode == MODE_CATEGORIES:
	viewCategories()
elif mode == MODE_CATEGORY:
	viewCategory(url)
elif mode == MODE_PROGRAM:
	viewProgram(url)
elif mode == MODE_VIDEO:
	startVideo(url)

xbmcplugin.endOfDirectory(pluginHandle)	
