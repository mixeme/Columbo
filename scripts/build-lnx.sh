#!/usr/bin/env sh

# Reference: https://pyinstaller.org/en/stable/usage.html#options

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ..;
echo "Project home: $PWD";

# Get a platform architecture
ARCH=$(uname -m);
echo "Detected platform architecture: $ARCH";

# Check the specified mode
if [ $# -gt 0 ];
then
	MODE=$1;
else
	MODE=onefile;
	echo "Build mode is not setup! Default one is used...";
fi
echo "Mode: $MODE";

# Create executable file
python3 -m PyInstaller \
	--name "columbo-$ARCH" \
	--$MODE \
	--windowed \
	--clean \
	--add-data="./gui:./gui" \
	--add-data="./icons:./icons" \
	--icon=icons/search.ico \
	main.py;

# Provide clean exit code
exit 0;
