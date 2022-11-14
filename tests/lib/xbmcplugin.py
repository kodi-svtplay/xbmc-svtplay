"""
Stub for 'xbmcplugin'
"""

directory_items = []
resolved_list_items = []

SORT_METHOD_UNSORTED = "a"
SORT_METHOD_LABEL = "b"
SORT_METHOD_DATEADDED = "c"

def addDirectoryItem(plugin_handle, url, list_item, folder):
  directory_items.append((url, list_item, folder))

def endOfDirectory(plugin_handle, cacheToDisc):
  pass

def getDirectoryItems():
  """This function is only for testing purposes"""
  return directory_items

def getDirectoryItem(pos):
  """This function is only for testing purposes"""
  return directory_items[pos]

def getRandomDirectoryItem():
  """This function is only for testing purposes"""
  import random
  return random.choice(directory_items)

def clearDirectoryItems():
  """This function is only for testing purposes"""
  directory_items.clear()

def setContent(plugin_handle, content):
  pass

def setResolvedUrl(plugin_handle, succeeded, list_item):
  resolved_list_items.clear()
  resolved_list_items.append(list_item)

def getResolvedListItemPath():
  return resolved_list_items[0].getPath()

def addSortMethod(plugin_handle, sort_method):
  pass