# -*- coding: utf-8 -*-
import xbmcaddon
import CommonFunctions
import re
import urllib

common = CommonFunctions
addon = xbmcaddon.Addon("plugin.video.svtplay")
THUMB_SIZE = "extralarge"

# Available bandwidths
BANDWIDTH = [300, 500, 900, 1600, 2500, 5000]

def getPage(url):
  if not url.startswith("/") and not url.startswith("http://"):
    url = "/" + url

  result = common.fetchPage({ "link": url })
  
  if result["status"] == 200:
    return result["content"]

  if result["status"] == 500:
    common.log("redirect url: %s" %result["new_url"])
    common.log("header: %s" %result["header"])
    common.log("content: %s" %result["content"])
    return None


def convertChar(char):
  if char == "&Aring;":
    return "Å"
  elif char == "&Auml;":
    return "Ä"
  elif char == "&Ouml;":
    return "Ö"
  else:
    return char


def convertDuration(duration):
  """
  Converts SVT's duration format to XBMC friendly format (minutes).

  SVT has the following format on their duration strings:
  1 h 30 min
  1 min 30 sek
  1 min
  """

  match = re.match(r'(^(\d+)\sh)*(\s*(\d+)\smin)*(\s*(\d+)\ssek)*', duration)

  dhours = 0
  dminutes = 0
  dseconds = 0

  if match.group(1):
    dhours = int(match.group(2)) * 60

  if match.group(3):
    dminutes = int(match.group(4))
 
  if match.group(5):
    dseconds = int(match.group(6)) / 60

  return str(dhours + dminutes + dseconds) 


def getUrlParameters(arguments):
  """
  Return URL parameters as a dict from a query string
  """
  params = {}

  if arguments:
    
      start = arguments.find("?") + 1
      pairs = arguments[start:].split("&")

      for pair in pairs:

        split = pair.split("=")

        if len(split) == 2:
          params[split[0]] = split[1]
  
  return params


def tabExists(html, tabname):
  """
  Check if a specific tab exists in the DOM.
  """
  return elementExists(html, "div", { "data-tabname": tabname})


def elementExists(html, etype, attrs):
  """
  Check if a specific element exists in the DOM.
  """

  htmlelement = common.parseDOM(html, etype, attrs = attrs)

  return len(htmlelement) > 0


def prepareThumb(thumbnail):
  """
  Returns a thumbnail with size THUMB_SIZE
  """
  common.log("old thumbnail: " + thumbnail)
  if not thumbnail.startswith("http://"):
    thumbnail = "http://www.svtplay.se" + thumbnail
  thumbnail = re.sub(r"/small|medium|large|extralarge/", "/"+THUMB_SIZE+"/", thumbnail)
  common.log("new thumbnail: " + thumbnail)
  return thumbnail


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
    """
    common.log("Stripping file: " + videoUrl)

    ufile = urllib.urlopen(videoUrl)
    lines = ufile.readlines()

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
          match = re.match(r'.*BANDWIDTH=(\d+).+', line)
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
  low_bandwidth  = int(float(addon.getSetting("bandwidth")))
  high_bandwidth = getHighBw(low_bandwidth)
  
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
      match = re.match(r'.*BANDWIDTH=(\d+)000.+', line)
      if match:
        if low_bandwidth < int(match.group(1)) < high_bandwidth:
          common.log("Found stream with bandwidth " + match.group(1) + " for selected bandwidth " + str(low_bandwidth))
          found = True
  
  f.close()

  if found:
    hlsurl = hlsurl.rstrip()
    common.log("Returned stream url: " + hlsurl)
    return (hlsurl, '')
  else:
    errormsg = "No stream found for bandwidth setting " + str(low_bandwidth)
    common.log(errormsg)
    return (None, errormsg)


def getHighBw(low):
  """
  Returns the higher bandwidth boundary
  """
  i = BANDWIDTH.index(low)
  return BANDWIDTH[i+1]


def getSetting(setting):
  return True if addon.getSetting(setting) == "true" else False
