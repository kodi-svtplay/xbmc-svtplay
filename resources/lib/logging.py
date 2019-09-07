import xbmc # pylint: disable=import-error

def log(msg, loglevel=xbmc.LOGDEBUG):
    xbmc.log("%s %s" % ("[plugin.video.svtplay] ", str(msg)), loglevel)

def error(msg):
    log(msg, xbmc.LOGERROR)