"""
Stub for module 'xbmc'
"""

LOGNOTICE = 10
PLAYLIST_MUSIC = 0
PLAYLIST_VIDEO = 1
LOGDEBUG = 1
LOGERROR = 2

def log(msg, level=None):
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  if level == LOGERROR:
    print("{} {} {}".format(FAIL, msg, ENDC))
  print(msg)

class Player:

  def isPlaying(self):
    return True

  def showSubtitles(self, show):
    pass

class PlayList:

  def __init__(self, list_id):
    self.__list_id = list_id
    self.__items = []

  def add(self, url, item):
    self.__items.append((url, item))

  def size(self):
    return len(self.__items)

  def dump(self):
    return str(self.__items)

class Keyboard:

  def __init__(self, heading):
    pass

  def doModal(self):
    pass

  def getText(self):
    pass