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

FILES=`git ls-files`

for FILE in $FILES; do
  cp --parent $FILE $DEPLOY_DIR
done
