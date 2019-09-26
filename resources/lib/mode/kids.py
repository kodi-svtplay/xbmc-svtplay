
from resources.lib import logging
from resources.lib import svt
from resources.lib.mode.common import Common

class Kids:

    def __init__(self, addon, plugin_url, plugin_handle, default_fanart, settings):
        logging.log("Starting Kids mode")
        self.common = Common(addon, plugin_url, plugin_handle, default_fanart, settings)

    def route(self, mode, url, params, page):
        if not mode:
            self.list_kids_section()
        elif mode == self.common.MODE_PROGRAM:
            self.view_episodes(url)
            self.common.add_clip_dir_item(url)
        elif mode == self.common.MODE_VIDEO:
            self.start_video(url)

    def view_episodes(self, url):
        logging.log("View episodes for {}".format(url))
        episodes = svt.getEpisodes(url.split("/")[-1])
        self.common.view_episodes(episodes)

    def view_clips(self, url):
        logging.log("View clips for {}".format(url))
        clips = svt.getClips(url.split("/")[-1])
        self.common.view_clips(clips)

    def list_kids_section(self):
        programs = svt.getProgramsForGenre("barn")
        if not programs:
            return
        for program in programs:
            mode = self.common.MODE_PROGRAM
            if program["type"] == "video":
                mode = self.common.MODE_VIDEO
            self.common.create_dir_item(program, mode)
    
    def start_video(self, video_id):
        video_json = svt.getVideoJSON(video_id)
        self.common.start_video(video_json)

        