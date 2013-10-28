# XBMC SVT Play addon

With this addon you can stream content from SVT Play (svtplay.se).
The plugin fetches the video URL from the SVT Play website and feeds it to the XBMC video player. HLS (m3u8) is the preferred video format by the plugin.

It requires XBMC 12.0 (frodo) to function.

**Created by nilzen.**

## Explaination of options

* (General) Show subtitles
  * Force programs to start with subtitles enabled. Subtitles can till be toggled on/off by using XBMC's controller shortcuts.
* (General) Show both clips and episodes for programs
  * By default the addon only displays episodes of a program. If this option is enable, the addon will show one section with episodes and one with clips (if available) for the program. If this setting is not enabled clips can only be found by using the search feature.
* (Advanced) Don't use avc1.77.30 streams
  * Forces the addon to choose the stream that supports the highest bandwidth but does not use the avc1.77.30 profile.
* (Advanced) Set bandwidth manually
  * Forces the addon to choose stream according to the set bandwidth. This option can be used to force lower resolution streams on devices with lower bandwidth capacity (i.e mobile devices). This option can only be used if "Don't use avc1.77.30 streams" is disabled.

## Known issues:

* Video playback may stutter on Apple TV2  and Raspberry Pi due to the use of the h264 profile avc1.77.30
  * Use the advanced plugin option "Don't use avc1.77.30 streams" to workaround this issue. This will force SD content only. Note that HD video is not supported on Apple TV 2 anymore due to changes by SVT.

## Donate:

If you like this addon, feel free to donate a small amount to the developers so we can keep on coding this together with a beer. :)

<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----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-----END PKCS7-----
">
<input type="image" src="https://www.paypalobjects.com/en_US/SE/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form>
