import xbmcgui # pylint: disable=import-error
import xbmcplugin # pylint: disable=import-error

try:
  # Python 2
  from urllib import urlencode
except ImportError:
  # Python 3
  from urllib.parse import urlencode

class Common:
    MODE_VIDEO = "video"

    def __init__(self, addon, plugin_url, plugin_handle, default_fanart):
        self.addon = addon
        self.plugin_url = plugin_url
        self.plugin_handle = plugin_handle
        self.default_fanart = default_fanart

    def add_directory_item(self, title, params, thumbnail="", folder=True, live=False, info=None):
        list_item = xbmcgui.ListItem(title)
        if live:
            list_item.setProperty("IsLive", "true")
        if not folder and params["mode"] == self.MODE_VIDEO:
            list_item.setProperty("IsPlayable", "true")
        fanart = info.get("fanart", "") if info else self.default_fanart
        poster = info.get("poster", "") if info else ""
        if info:
            if "fanart" in info:
                del info["fanart"] # Unsupported by ListItem
            if "poster" in info:
                del info["poster"] # Unsupported by ListItem
            list_item.setInfo("video", info)
        list_item.setArt({
            "fanart": fanart,
            "poster": poster if poster else thumbnail,
            "thumb": thumbnail
        })
        url = self.plugin_url + '?' + urlencode(params)
        xbmcplugin.addDirectoryItem(self.plugin_handle, url, list_item, folder)