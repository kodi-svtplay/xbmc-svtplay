from __future__ import absolute_import,unicode_literals
import time
import xbmc # pylint: disable=import-error
import xbmcgui # pylint: disable=import-error
import xbmcplugin # pylint: disable=import-error

from resources.lib import helper

class Playback:

    def __init__(self, plugin_handle):
        self.plugin_handle = plugin_handle
    
    def play_video(self, video_url, subtitle_url, show_subtitles):
        is_hls = video_url.split("?")[0].endswith("m3u8")
        mime_type = "application/vnd.apple.mpegurl" if is_hls else "application/xml+dash"
        manifest_type = "hls" if is_hls else "mpd"
        player = xbmc.Player()
        start_time = time.time()
        listitem = xbmcgui.ListItem(path=video_url)
        listitem.setMimeType(mime_type)
        listitem.setContentLookup(False)
        listitem.setProperty("inputstream", "inputstream.adaptive")
        listitem.setProperty("inputstream.adaptive.manifest_type", manifest_type)
        xbmcplugin.setResolvedUrl(self.plugin_handle, True, listitem)
        if subtitle_url:
            while not player.isPlaying() and time.time() - start_time < 10:
                time.sleep(1.)
                player.setSubtitles(subtitle_url)
            if not show_subtitles:
                player.showSubtitles(False)    