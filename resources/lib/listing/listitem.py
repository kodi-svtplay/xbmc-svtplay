# -*- coding: utf-8 -*-
from __future__ import absolute_import,unicode_literals


class PlayItem(object):
    """
    A generic SVT Play list item
    """
    VIDEO_ITEM = "video"
    SHOW_ITEM = "show"

    def __init__(self, title, id, thumbnail, geo_restricted, item_type, info={}):
        self.title = title
        self.id = id
        self.thumbnail = thumbnail
        self.geo_restricted = geo_restricted
        self.item_type = item_type
        self.info = info

class VideoItem(PlayItem):
    """
    A video list item.
    """
    def __init__(self, title, video_id, thumbnail, geo_restricted, info={}, fanart=""):
        super(VideoItem, self).__init__(title, video_id, thumbnail, geo_restricted, PlayItem.VIDEO_ITEM, info)
        self.fanart = fanart

class ShowItem(PlayItem):
    """
    A show list item, which means a folder containing VideoItems
    """
    def __init__(self, title, show_id, thumbnail, geo_restricted):
        super(ShowItem, self).__init__(title, show_id, thumbnail, geo_restricted, PlayItem.SHOW_ITEM, info={})