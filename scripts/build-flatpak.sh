#! /bin/bash

cd "$(dirname "$0")";

# Prepare source folders
[ -d src ] && echo "+ Remove src/" && rm -R src;
mkdir src;

DIRS="core icons gui";
for i in $DIRS;
do
	echo "+ Copy $i";
	rsync -av --exclude="__pycache__" ../../$i/ src/$i;
done
cp ../../main.py src/;

# Build
#flatpak-builder --verbose --force-clean build-dir ru.mixeme.Columbo.yaml

MANIFEST=$PWD/ru.mixeme.Columbo.yaml;
BUILD_DIR=~/.cache/columbo;

cd $BUILD_DIR;

# Build & install
echo "+ Build";
flatpak-builder --user --install --force-clean build-dir $MANIFEST
#
# Run app
# flatpak run ru.mixeme.Columbo
#
# Debug app
# # flatpak run --command="bash" ru.mixeme.Columbo
#
# Export to the local repo
# flatpak build-export repo build
#
# Create single-file bundles
# flatpak build-bundle -v repo columbo.flatpak ru.mixeme.Columbo
# flatpak build-bundle -v repo columbo2.flatpak ru.mixeme.Columbo --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo

