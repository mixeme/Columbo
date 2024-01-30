#!/usr/bin/env sh

# Clear a previous installation
#   sudo rm -R /opt/Columbo; sudo rm -R Columbo; sudo rm /usr/local/bin/columbo
#
# Make a new installation
#   sudo apt install -y git && git clone -b dev https://github.com/mixeme/Columbo.git && sudo bash Columbo/scripts/install-git.sh [source | binary | standalone]

# Check input arguments
if [ "$#" -eq 0 ];
then
  COMMAND=source;
  echo "No arguments are provided. Default option '$COMMAND' is used";
else
  COMMAND=$1;
fi

# Check command value
case $COMMAND in
	source )
	    echo "Columbo will be installed as source";
	;;
	binary )
	  echo "Columbo will be installed as a regular binary";
	;;
	standalone )
	  echo "Columbo will be installed as a standalone binary";
	;;
	* )
	echo "Unknown command ${COMMAND}";
	echo "Possible commands: source (default) | binary | standalone";
	echo "Exit";
	exit 1;
esac

# Switch to scripts location
cd "$(dirname "$0")" || exit 1;

# Setup variables
## Build
ARCH=$(uname -m);
BIN_NAME="columbo-$ARCH";
## Paths
COLUMBO_HOME="/opt/Columbo";
SYSTEM_BIN="/usr/local/bin/columbo";
## Show defined values
echo "Platform: $ARCH";
echo "Columbo home: $COLUMBO_HOME";

# Prepare environment
echo "+ Install system packages...";
apt update -y && apt install -y rsync python3 python3-pip python3-pyqt5;
echo "+ Install Python packages...";
pip install --upgrade pyinstaller;
# If `pip` command is unknown then use
# 	python -m pip install --upgrade pyinstaller

# Build routine
build() {
    # Run build script
    bash build-lnx.sh "$1";

    # Resolve variables
    COPY_SOURCE="../dist/$BIN_NAME";
    case $1 in
      onedir )
        COPY_TARGET="$COLUMBO_HOME";
        COLUMBO_BIN="$COLUMBO_HOME/$BIN_NAME";
      ;;
      onefile )
        COPY_TARGET=$SYSTEM_BIN;
        COLUMBO_BIN=$SYSTEM_BIN;
      ;;
    esac

    # Copy binary
    echo "+ Copy binary from $COPY_SOURCE to $COPY_TARGET";
    cp -R "$COPY_SOURCE" "$COPY_TARGET";

    # Make binary executable
    echo "+ Make $COLUMBO_BIN executable";
		chmod +x "$COLUMBO_BIN";

    # Create symlink for binary in Columbo home
    RUN_MESSAGE="\t$(basename $SYSTEM_BIN) | $SYSTEM_BIN";
    if [ "$1" = "onedir" ];
    then
      echo "+ Create symlink for $COLUMBO_BIN as $SYSTEM_BIN";
      ln -s "$COLUMBO_BIN" $SYSTEM_BIN;
      RUN_MESSAGE="$RUN_MESSAGE | $COLUMBO_BIN";
    fi

    # Show message for application run
		echo "Run Columbo as";
		echo -e "$RUN_MESSAGE";
}

# Resolve command
case $COMMAND in
	source )
	  COLUMBO_PY="$COLUMBO_HOME/main.py";
	  echo "+ Copy sources to $COLUMBO_HOME";
	  rsync -av --exclude=".*" ../../Columbo/ $COLUMBO_HOME;
	  echo "+ Make script executable";
		chmod +x $COLUMBO_PY;
		echo "Run Columbo as";
		echo -e "\t$COLUMBO_PY | python3 $COLUMBO_PY";

		echo "#! /bin/bash
exec python3 $COLUMBO_PY
exit 0;
" > $SYSTEM_BIN;

	;;
	binary )
	  echo "+ Build a regular binary...";
		build onedir;
	;;
	standalone )
	  echo "+ Build a standalone binary...";
	  build onefile;
	;;
esac

# Remove installation folder
echo "Clean installation folder";
rm -R ../../Columbo;

# Exit
echo "Enjoy Columbo!";
exit 0;
