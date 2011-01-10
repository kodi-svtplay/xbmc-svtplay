# -*- coding: utf-8 -*-
import os
import urllib
import urllib2
import xbmcgui
import xbmcplugin
import xbmcaddon

from xml.dom.minidom import parse, parseString

# The SETTINGS_ contstants should be read from addon settings instead
SETTINGS_HIGHEST_BITRATE = float(100000000)
SETTINGS_MAX_ITEMS_PER_PAGE = 50

TEXT_NEXT_PAGE = "Nästa sida"

MODE_DEVICECONFIG = "deviceconfig"
MODE_TITLE_LIST = "title"
MODE_TEASER_LIST = "teaser"
MODE_VIDEO_LIST = "video"

BASE_URL_TEASER = "http://xml.svtplay.se/v1/teaser/list/"
BASE_URL_TITLE = "http://xml.svtplay.se/v1/title/list/"
BASE_URL_VIDEO = "http://xml.svtplay.se/v1/video/list/"

NS_MEDIA = "http://search.yahoo.com/mrss/"
NS_PLAYOPML = "http://xml.svtplay.se/ns/playopml"
NS_PLAYRSS = "http://xml.svtplay.se/ns/playrss"
NS_OPENSEARCH = "http://a9.com/-/spec/opensearch/1.1/"

def get_child_outlines(node):
	for child in node.childNodes:
		if child.nodeType == child.ELEMENT_NODE and child.nodeName == "outline":
			yield child

def deviceconfiguration(node=None, target="", path=""):
	
	if node is None:
		node = load_xml("http://svtplay.se/mobil/deviceconfiguration.xml").documentElement.getElementsByTagName("body")[0]
		
	for outline in get_child_outlines(node):

		title = outline.getAttribute("text").encode('utf-8')		
		next_path = path + title + "/"
		
		if target == path:

			type = outline.getAttribute("type")

			if path + title == "Karusellen" \
			or path + title == "Sök" \
			or path + title == "Hjälpmeny" \
			or not (type == "rss" or type == "menu"):
				continue

			thumbnail = outline.getAttributeNS(NS_PLAYOPML, "thumbnail")
			ids = outline.getAttributeNS(NS_PLAYOPML, "contentNodeIds")
			xml_url = outline.getAttribute("xmlUrl")
			
			if ids:
				params = { "mode": MODE_TITLE_LIST, "ids": ids }
			elif xml_url:
				if xml_url.startswith(BASE_URL_TEASER):
					params = { "mode": MODE_TEASER_LIST, "url": xml_url }
				elif xml_url.startswith(BASE_URL_TITLE):
					params = { "mode": MODE_TITLE_LIST, "url": xml_url }
				elif xml_url.startswith(BASE_URL_VIDEO):
					params = { "mode": MODE_VIDEO_LIST, "url": xml_url }
				else:
					xbmc.log("unknown url: " + xml_url)
			else:
				params = { "mode": MODE_DEVICECONFIG, "path": next_path }

			add_directory_item(title, params, thumbnail)

		else:
			if target.startswith(next_path):
				deviceconfiguration(outline, target, next_path)

def title_list(ids="", url="", offset=1, list_size=0):

	if ids:
		url = BASE_URL_TITLE + ids

	doc = load_xml(get_offset_url(url, offset))

	for item in doc.getElementsByTagName("item"):

		if list_size < SETTINGS_MAX_ITEMS_PER_PAGE:

			title = item.getElementsByTagName("title")[0].childNodes[0].data
		
			thumb = None
			thumbnail_nodes = item.getElementsByTagNameNS(NS_MEDIA, "thumbnail")
		
			if thumbnail_nodes:
				thumb = thumbnail_nodes[0].getAttribute("url")
		
			id = item.getElementsByTagNameNS(NS_PLAYRSS, "titleId")[0].childNodes[0].data

			params = { "mode": MODE_VIDEO_LIST, "ids": id }
		
			list_size += 1
			offset += 1

			add_directory_item(title, params, thumb)

	total_results = int(doc.getElementsByTagNameNS(NS_OPENSEARCH, "totalResults")[0].childNodes[0].data)
	items_per_page = int(doc.getElementsByTagNameNS(NS_OPENSEARCH, "itemsPerPage")[0].childNodes[0].data)

	if total_results > offset and offset < SETTINGS_MAX_ITEMS_PER_PAGE:
		title_list(ids, url, offset, list_size)
	elif total_results > offset:
		params = { "mode": MODE_TITLE_LIST, "ids": ids, "url": url, "offset": offset }
		add_directory_item(TEXT_NEXT_PAGE, params)
	
def video_list(ids="", url="", offset=1, list_size=0):

	if ids:
		url = BASE_URL_VIDEO + ids

	doc = load_xml(get_offset_url(url, offset))
		
	for item in doc.getElementsByTagName("item"):
		
		if list_size < SETTINGS_MAX_ITEMS_PER_PAGE:
		
			media = get_media_content(item)
			thumb = get_media_thumbnail(item)

			title = media.getElementsByTagNameNS(NS_MEDIA, "title")[0].childNodes[0].data

			params = { "url": media.getAttribute("url") }
		
			list_size += 1
			offset += 1

			add_directory_item(title, params, thumb.getAttribute("url"), False)

	total_results = int(doc.getElementsByTagNameNS(NS_OPENSEARCH, "totalResults")[0].childNodes[0].data)
	items_per_page = int(doc.getElementsByTagNameNS(NS_OPENSEARCH, "itemsPerPage")[0].childNodes[0].data)

	if total_results > offset and list_size < SETTINGS_MAX_ITEMS_PER_PAGE:
		video_list(ids, url, offset, list_size)
	elif total_results > offset:
		params = { "mode": MODE_VIDEO_LIST, "ids": ids, "url": url, "offset": offset }
		add_directory_item(TEXT_NEXT_PAGE, params)

def teaser_list(url):
	xbmc.log("parse teaser list: " + url)	

def get_offset_url(url, offset):
	if offset == 0:
		return url

	if url.find("?") == -1:
		return url + "?start=" + str(offset)
	else:
		return url + "&start=" + str(offset)

def get_media_thumbnail(node):

	content_list = node.getElementsByTagNameNS(NS_MEDIA, "content");

	for c in content_list:
		if c.getAttribute("type") == "image/jpeg":
			return c

	return None
	
def get_media_content(node):
 
	group = node.getElementsByTagNameNS(NS_MEDIA, "group")
	
	if group:
		content_list = group[0].getElementsByTagNameNS(NS_MEDIA, "content");
	else:
		content_list = node.getElementsByTagNameNS(NS_MEDIA, "content");
 
	content = None
 
	for c in content_list:
	
		if not c.getAttribute("bitrate"):
			continue
	
		bitrate = float(c.getAttribute("bitrate"))
		type = c.getAttribute("type")

		if type == 'application/vnd.apple.mpegurl':
			continue
		
		if not content or (bitrate > float(content.getAttribute("bitrate")) and bitrate <= SETTINGS_HIGHEST_BITRATE):
			content = c

	# probably a live stream, check framerate instead
	if not content:
			
		for c in content_list:
		
			if not c.getAttribute("framerate"):
				continue
		
			framerate = float(c.getAttribute("framerate"))
			type = c.getAttribute("type")

			if type == 'application/vnd.apple.mpegurl':
				continue
			
			if not content or framerate > float(content.getAttribute("framerate")):
				content = c
				
	return content
	
def add_directory_item(name, params={}, thumbnail=None, isFolder=True):

	li = xbmcgui.ListItem(name)

	if not thumbnail is None:
		li.setThumbnailImage(thumbnail)

	
	if isFolder == True:
		url = sys.argv[0] + '?' + urllib.urlencode(params)
	else:
		url = params["url"]

	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def parameters_string_to_dict(str):
	params = {}
	if str:
		pairs = str[1:].split("&")
		for pair in pairs:
			split = pair.split('=')
			if (len(split)) == 2:
				params[split[0]] = split[1]
	
	return params

def load_xml(url):
	xbmc.log(url)
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	xml = response.read()
	response.close()
	
	return parseString(xml)

params = parameters_string_to_dict(sys.argv[2])

mode = params.get("mode", None)
ids = params.get("ids",  "")
offset = int(params.get("offset",  "1"))
path = urllib.unquote_plus(params.get("path", ""))
url = urllib.unquote_plus(params.get("url",  ""))

if not sys.argv[2] or not mode:
	deviceconfiguration()
elif mode == MODE_DEVICECONFIG:
	deviceconfiguration(None, path)
elif mode == MODE_TEASER_LIST:
	teaser_list(url)
elif mode == MODE_TITLE_LIST:
	title_list(ids, url, offset)
elif mode == MODE_VIDEO_LIST:
	video_list(ids, url, offset)

xbmcplugin.endOfDirectory(int(sys.argv[1]))