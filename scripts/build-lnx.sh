#!/usr/bin/env sh

ARCH=$(uname -m)

python -m PyInstaller \
	--clean \
	--windowed \
	--onefile \
	--name columbo-$ARCH \
	--add-data="./gui:./gui" \
	--add-data="./icons:./icons" \
	--icon=icons/search.ico \
	main.py