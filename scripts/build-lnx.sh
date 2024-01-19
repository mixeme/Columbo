#!/usr/bin/env sh

# Reference: https://pyinstaller.org/en/stable/usage.html#options

# Change location to project home
cd $(dirname $0);
cd ..;
echo "Project home: $PWD";

# Get platform architecture
ARCH=$(uname -m);
echo "Detected platform architecture: $ARCH";

#
if [ $# -gt 0 ];
then
	MODE=$1;
else
	MODE=onefile;
fi

# Create executable file
python3 -m PyInstaller \
	--name columbo-$ARCH \
	--$MODE \
	--windowed \
	--clean \
	--add-data="./gui:./gui" \
	--add-data="./icons:./icons" \
	--icon=icons/search.ico \
	main.py;

exit 0;
