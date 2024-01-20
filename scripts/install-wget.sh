#!/usr/bin/env sh

# Clear a previous installation
#   sudo rm -R /opt/Columbo && rm install-wget.sh && sudo rm /usr/local/bin/columbo
#
# Make a new installation
#   wget https://github.com/mixeme/Columbo/raw/dev/scripts/install.sh && sudo bash [source | binary | standalone]

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
SCRIPT_PATH="$PWD/$(basename "$0")";

# Setup variables
## Repo
BRANCH=dev;
## Build
ARCH=$(uname -m);
BIN_NAME="columbo-$ARCH";
## Paths
APP_ROOT=/opt;
COLUMBO_HOME="$APP_ROOT/Columbo";
COLUMBO_PY="$COLUMBO_HOME/main.py";
COLUMBO_BIN="$COLUMBO_HOME/dist/$BIN_NAME";
SYSTEM_BIN=/usr/local/bin/columbo;
## Show defined values
echo "Script path: $SCRIPT_PATH";
echo "Branch: $BRANCH";
echo "Platform: $ARCH";
echo "Application root: $APP_ROOT";
echo "Columbo home: $COLUMBO_HOME";

# Prepare environment
echo "+ Install system packages...";
apt update -y && apt install -y git python3 python3-pip python3-pyqt5;
echo "+ Install Python packages...";
pip install --upgrade pyinstaller
# If `pip` command is unknown then use
# 	python -m pip install --upgrade pyinstaller

# Clone repo
echo "+ Clone Columbo repo...";
cd "$APP_ROOT" || exit 1;
git clone -b $BRANCH https://github.com/mixeme/Columbo.git;

# Build routine
build() {
    bash $COLUMBO_HOME/scripts/build-lnx.sh "$1";
    echo "+ Make $COLUMBO_BIN executable";
		chmod +x "$COLUMBO_BIN";
		echo "+ Create symlink for $COLUMBO_BIN as $SYSTEM_BIN";
		ln -s "$COLUMBO_BIN" $SYSTEM_BIN;
		echo "Run Columbo as";
		echo -e "\t$(basename $SYSTEM_BIN) | $SYSTEM_BIN | $COLUMBO_BIN";
}

# Resolve command
case $COMMAND in
	source )
	  echo "+ Make script executable...";
		chmod +x $COLUMBO_PY;
		echo "Run Columbo as";
		echo -e "\t$COLUMBO_PY | python3 $COLUMBO_PY";
	;;
	binary )
	  COLUMBO_BIN="$COLUMBO_BIN/$BIN_NAME";
	  echo "+ Build a regular binary...";
		build onedir;
	;;
	standalone )
	  echo "+ Build a standalone binary...";
	  build onefile;
	;;
esac

# Remove script
echo "Clean install script $SCRIPT_PATH";
rm "$SCRIPT_PATH";

# Exit
echo "Enjoy Columbo!";
exit 0;
