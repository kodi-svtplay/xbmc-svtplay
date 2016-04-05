# Maintenance

Owner: @nilzen

Maintainers: @linqcan, @nilzen

## Tests
The folder "tests" contain certain unit tests that can be run to verify some basic functionalty.

Especially, testSvt.py can be run to test the site crawler and verify if/what is broken.
```
cd tests
python2.7 -m unittest testSvt
```

## Deploy
Deploying code is done, preferly, via Github and Pull Requests.

* Fork xbmc/repo-plugins
* Make changes to plugin and push as normal to the xbmc-svtplay repo
* When ready for deploy, run deploy.sh towards your local fork of xbmc/repo-plugins
  * Make sure branch gotham is used as that is the target branch
  * Make sure you have synced (git pull) your local fork with upstream (xbmc/repo-plugins) before deploying
* Push to your GitHub fork
* Create PR towards xbmc/repo-plugins and branch gotham
