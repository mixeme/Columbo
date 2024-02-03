#!/usr/bin/env sh

# Make a new installation
#   sudo apt install -y git docker docker.io apparmor
#   git clone -b dev https://github.com/mixeme/Columbo.git && sudo bash Columbo/scripts/install-docker.sh [regular | standalone]

# Check input arguments
if [ "$#" -eq 0 ];
then
  COMMAND=regular;
  echo "No arguments are provided. Default option '$COMMAND' is used";
else
  COMMAND=$1;
fi

# Check command value
case $COMMAND in
	regular )
	  echo "Columbo will be build and installed as a regular binary";
	  MODE=onedir;
	;;
	standalone )
	  echo "Columbo will be build and installed as a standalone binary";
	  MODE=onefile;
	;;
	* )
	echo "Unknown command ${COMMAND}. Possible commands: regular (default) | standalone.
Exit";
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

# Source functions
source common.sh

check_previous;       # Remove a previous installation
build_docker $MODE;   # Build binary with Docker
install_app $MODE;    # Install binary to the system

# Remove installation folder
echo "Clean installation folder";
rm -R ../../Columbo;

# Exit
echo "Enjoy Columbo!";
exit 0;
