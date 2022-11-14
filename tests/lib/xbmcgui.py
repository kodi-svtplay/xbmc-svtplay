"""
Stub for 'xbmcgui'
"""

class ListItem:

  def __init__(self, label=None, path=""):
    self.__label = label
    self.path = path

  def getLabel(self):
    return self.__label

  def setThumbnailImage(self, path):
    self.__thumb = path

  def setPath(self, path):
    self.__path = path

  def setProperty(self, prop, value):
    pass

  def setInfo(self, content, info):
    pass

  def setArt(self, art):
    pass

  def addContextMenuItems(self, items):
    pass

  def getPath(self):
    return self.path