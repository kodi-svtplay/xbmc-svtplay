#!/bin/bash

# Use this script to deploy to the XBMC/Kodi
# plugins repo.

if [ "$#" -ne 1 ]; then
  echo "Missing argument for deploy dir!"
  echo "Usage: deploy.sh /my/dir/repo-plugins/plugin.video.svtplay/"
  exit 1
fi

# Exit on error
set -e

DEPLOY_DIR=$1

EXCLUDE_FILES="deploy.sh \
              ISSUE_TEMPLATE.md \
              CONTRIBUTING.md \
              tests/.gitignore \
              tests/testFM.py \
              tests/testHelper.py \
              tests/testSvt.py \
              tests/lib/CommonFunctions.py \
              tests/lib/xbmc.py \
              tests/lib/xbmcaddon.py \
              tests/lib/xbmcgui.py"

FILES=`git ls-files`

for FILE in $FILES; do
  if [[ $EXCLUDE_FILES =~ $FILE ]]; then
    echo "Skipping excluded file $FILE"
    continue
  fi
  echo "Copying $FILE to $DEPLOY_DIR$FILE"
  cp --parent $FILE $DEPLOY_DIR
done
