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
    echo "
Build mode was not specified as an argument or as an environment variable MODE. Choose build mode:
  [1] onedir (one executable file and a folder with supplementary files, works faster)
  [2] onefile (all in one executable file, works slower)
";

	read -p "Enter a number of option or just press ENTER for 'onedir' option: " OPTION;
	case $OPTION in
	  1 )
	    MODE=onedir;
	  ;;
	  2 )
	    MODE=onefile;
	  ;;
	  * )
	    MODE=onedir;
	  ;;
	esac
fi
echo "Mode: $MODE";

# Create executable file
python3 -m PyInstaller \
	--name "columbo-$ARCH" \
	--$MODE \
	--windowed \
	--noconfirm \
	--clean \
	--add-data="./gui:./gui" \
	--add-data="./icons:./icons" \
	--icon=icons/search.ico \
	main.py;

# Provide clean exit code
exit 0;
