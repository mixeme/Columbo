#!/usr/bin/env bash

# Reference: https://pyinstaller.org/en/stable/usage.html#options

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ..;
echo "Project home: $PWD";

# Get a platform architecture
ARCH=$(uname -m);
BIN_NAME="columbo-$ARCH";
echo "Detected platform architecture: $ARCH";

# Check the specified mode
if [ $# -gt 0 ];
then
	MODE=$1;
else
  if ! [ -v MODE ];   # If MODE is not defined in the environment (is used in Docker image)
  then
    echo "
Build mode was not specified as an argument or as an environment variable MODE. Choose build mode:
  [1] onedir (one executable file and a folder with supplementary files, works faster)
  [2] onefile (all in one executable file, works slower)
";

    read -p "Enter a number of an option or just press ENTER for default 'onedir' option: " OPTION;
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
fi
echo "Mode: $MODE";

if [ -v TAG ];
then
	echo "Build tag: $TAG";
	BIN_NAME="$BIN_NAME-$TAG";
else
	echo "Build tag is not defined";
fi

# Create executable file
echo "Target binary name: $BIN_NAME";
echo "+ Launch PyInstaller";
python3 -m PyInstaller \
	--name $BIN_NAME \
	--$MODE \
	--windowed \
	--noconfirm \
	--clean \
	--add-data="./src/gui:./src/gui" \
	--add-data="./resources/icons:./resources/icons" \
	--icon=resources/icons/search.ico \
	src/main.py;

# Delete temp folder
echo "+ Remove 'build' folder";
rm -R build;
echo "+ Remove .spec";
rm $BIN_NAME.spec;

# Create an archive with binary
if [ "$MODE" = "onedir" ] && [ -d "$BIN_NAME" ];
then
  echo "+ Pack a folder with binary...";
  cd dist || exit 1;
  tar -czf "$BIN_NAME".tar.gz "$BIN_NAME";
  rm -R "$BIN_NAME";
  echo "+ Columbo is packed to dist/$BIN_NAME.tar.gz";
fi

# Provide clean exit code
exit 0;

