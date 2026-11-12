#!/bin/sh
# Copies the web game (index.html, the vendored three.js and fonts, the vehicle models) into the app bundle,
# at <App>.app/web/. Runs on every build, so the app always has the current version of the game.
set -e
REPO="${SRCROOT}/.."
DEST="${TARGET_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/web"
mkdir -p "$DEST"
rsync -a --delete --exclude '.DS_Store' "$REPO/index.html" "$DEST/"
rsync -a --delete --exclude '.DS_Store' "$REPO/vendor" "$DEST/"
mkdir -p "$DEST/assets"
rsync -a --delete --exclude '.DS_Store' --exclude 'README.txt' "$REPO/assets/models" "$DEST/assets/"
echo "Copied the web game to $DEST"
