#!/usr/bin/env sh

# Change location to project home
cd $(dirname $0);
cd ..;
echo "Project home:" $PWD;

# Get platform architecture
ARCH=$(uname -m);
echo "Detected platform architecture:" $ARCH

# Create executable file
python -m PyInstaller \
	--clean \
	--windowed \
	--onefile \
	--name columbo-$ARCH \
	--add-data="./gui:./gui" \
	--add-data="./icons:./icons" \
	--icon=icons/search.ico \
	main.py;

exit 0;
