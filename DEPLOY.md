# Maintenance

Owner: @nilzen
Maintainers: @linqcan, @nilzen

Deploying code is done, preferly, via Github and Pull Requests.

* Fork xbmc/repo-plugins
* Make changes to plugin and push as normal to the xbmc-svtplay repo
* When ready for deploy, run deploy.sh towards your local fork of xbmc/repo-plugins
** Make sure branch gotham is used as that is the target branch
** Make sure you have synced (git pull) your local fork with upstream (xbmc/repo-plugins) before deploying
* Push to your GitHub fork
* Create PR towards xbmc/repo-plugins and branch gotham
