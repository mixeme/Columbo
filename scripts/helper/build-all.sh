#!/usr/bin/env bash

cd "$(dirname "$0")" || exit 1;

# Docker
## onedir type
bash ./docker.sh deb11 binary onedir
bash ./docker.sh deb10 binary onedir
bash ./docker.sh centos7 binary onedir

## onefile type
bash ./docker.sh deb11 binary onefile
bash ./docker.sh deb10 binary onefile
bash ./docker.sh centos7 binary onefile

# Flatpak
bash ./flatpak.sh build
bash ./flatpak.sh export
bash ./flatpak.sh clean


