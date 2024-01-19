#!/usr/bin/env sh

# sudo rm -R /opt/Columbo && rm install.sh && sudo rm /usr/local/bin/columbo
# wget https://github.com/mixeme/Columbo/raw/dev/scripts/install.sh && sudo bash [source | binary | standalone]

if [ "$#" -eq 0 ];
then
  COMMAND=source;
  echo "No arguments are provided. Use default option '$COMMAND'";
else
  COMMAND=$1;
fi

case $COMMAND in
	source )
	    echo "Columbo will be installed as source";
	;;
	binary )
	  echo "Columbo will be installed as regular binary";
	;;
	standalone )
	  echo "Columbo will be installed as standalone binary";
	;;
	* )
	echo "Unknown command ${COMMAND}";
	echo "Possible commands: source (default) | binary | standalone";
esac

cd "$(dirname "$0")" || exit 1;

BRANCH=dev;
ARCH=$(uname -m);
BIN_NAME="columbo-$ARCH";
APP_ROOT=/opt;
COLUMBO_HOME="$APP_ROOT/Columbo";
COLUMBO_PY="$COLUMBO_HOME/main.py";
COLUMBO_BIN="$COLUMBO_HOME/dist/$BIN_NAME";
SYSTEM_BIN=/usr/local/bin/columbo;

echo "Branch: $BRANCH";
echo "Platform: $ARCH";
echo "Application root: $APP_ROOT";
echo "Columbo home: $COLUMBO_HOME";

echo "+ Install system packages...";
apt update -y && apt install -y git python3 python3-pip python3-pyqt5;
echo "+ Install Python packages...";
pip install --upgrade pyinstaller

# If `pip` command is unknown then
# 	python -m pip install --upgrade pyinstaller

echo "+ Clone Columbo repo...";
cd "$APP_ROOT" || exit 1;
git clone -b $BRANCH https://github.com/mixeme/Columbo.git;


build() {
    bash $COLUMBO_HOME/scripts/build-lnx.sh "$1";
    echo "+ Make $COLUMBO_BIN executable";
		chmod +x "$COLUMBO_BIN";
		echo "+ Create symlink for $COLUMBO_BIN as $SYSTEM_BIN";
		ln -s "$COLUMBO_BIN" $SYSTEM_BIN;
}

case $COMMAND in
	source )
	  echo "+ Make script executable...";
		chmod +x $COLUMBO_PY;
		echo "Run Columbo with";
		echo -e "\tpython3 $COLUMBO_PY";
		#echo "+ Make main script executable...";
		#ln -s $COLUMBO_PY $SYSTEM_BIN;
	;;
	binary )
	  COLUMBO_BIN="$COLUMBO_BIN/$BIN_NAME";
	  echo "+ Build regular binary...";
		build onedir;
	;;
	standalone )
	  echo "+ Build standalone binary...";
	  build onefile;
	;;
esac
