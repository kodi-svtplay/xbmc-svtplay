# -*- coding: utf-8 -*-
from __future__ import absolute_import,unicode_literals
import os
import sys
import xbmc # pylint: disable=import-error
import xbmcaddon # pylint: disable=import-error
import xbmcplugin # pylint: disable=import-error

from resources.lib import helper
from resources.lib import logging
from resources.lib.listing.router import Router
from resources.lib.settings import Settings

# plugin setup
PLUGIN_HANDLE = int(sys.argv[1])
PLUGIN_URL = sys.argv[0]
PLUGIN_PARAMS = sys.argv[2]
addon = xbmcaddon.Addon("plugin.video.svtplay")
settings = Settings(addon)
xbmcplugin.setContent(PLUGIN_HANDLE, "tvshows")
xbmcplugin.addSortMethod(PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
xbmcplugin.addSortMethod(PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
DEFAULT_FANART = os.path.join(
  xbmc.translatePath(addon.getAddonInfo("path") + "/resources/images/"),
  "background.png")

# Main segment of script
ARG_PARAMS = helper.getUrlParameters(PLUGIN_PARAMS)
logging.log("Addon params: {}".format(ARG_PARAMS))
ARG_MODE = ARG_PARAMS.get("mode")
ARG_URL = ARG_PARAMS.get("url", "")
ARG_PAGE = ARG_PARAMS.get("page")
if not ARG_PAGE:
  ARG_PAGE = "1"

if settings.kids_mode and not ARG_PARAMS:
  logging.log("Kids mode, redirecting to genre Barn")
  ARG_MODE = Router.MODE_CATEGORY
  ARG_URL = "barn"

router = Router(addon, PLUGIN_URL, PLUGIN_HANDLE, DEFAULT_FANART, settings)
router.route(ARG_MODE, ARG_URL, ARG_PARAMS, int(ARG_PAGE))

cacheToDisc = True
if not ARG_PARAMS:
  # The top-level menu should not be cached as it will prevent
  # Kids mode to take effect when toggled on.
  cacheToDisc = False
xbmcplugin.endOfDirectory(PLUGIN_HANDLE, cacheToDisc=cacheToDisc)
