# Kodi SVT Play Addon

With this addon you can stream content from SVT Play (svtplay.se).

The plugin fetches the video URL from the SVT Play website and feeds it to the Kodi video player.

HLS (m3u8) is the preferred video format by the plugin.

It requires Kodi (XBMC) 13.0 (Gotham) to function.

## Known Issues
### Live broadcasts does not work on iOS, ATV2, OSX and Android
This is due to encrypted HLS streams not being supported. See this issue ticket for more info [#98](https://github.com/nilzen/xbmc-svtplay/issues/98).

## Development

### Running tests
The module responsible for parsing the SVT Play website has a couple of tests that can be run to verify its functionality.

To run these tests, execute the following commands from this repository's root folder:
```
cd tests
python -m unittest testSvt
```
