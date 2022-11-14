"""
Mock for 'xbmcaddon'
"""

class Addon:

  def __init__(self, id=None):
    self.id = id
    self.version = 1.0
    self.settings = {}


  def getAddonInfo(self, id):
    if id == self.id:
      return self.id
    else:
      return "no info"

  def getLocalizedString(self, id_num):
    return str(id_num)

  def getSetting(self, setting):
    return "false"
