#!/usr/bin/env sh

# wget https://github.com/mixeme/Columbo/raw/dev/scripts/install.sh && sudo bash [source | binary | standalone]

if [ "$#" -eq 0 ];
then
  COMMAND=source;
  echo "No arguments are provided. Use default option" $COMMAND;
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
APP_ROOT=/opt;
COLUMBO_HOME="$APP_ROOT/Columbo";
COLUMBO_PY="$COLUMBO_HOME/main.py";
COLUMBO_BIN="$COLUMBO_HOME/dist/columbo-$ARCH";

echo "+ Install system packages...";
apt update -y && apt install -y git python3 python3-pip python3-pyqt5;
echo "+ Install Python packages...";
pip install --upgrade pyinstaller

# If `pip` command is unknown then
# 	python -m pip install --upgrade pyinstaller

echo "+ Clone Columbo repo...";
cd "$APP_ROOT" || exit 1;
git clone -b $BRANCH https://github.com/mixeme/Columbo.git;

case $COMMAND in
	source )
	  echo "+ Make main script executable...";
		chmod +x $COLUMBO_PY;
		echo "+ Make main script executable...";
		ln -s $COLUMBO_PY /usr/local/bin/columbo;
	;;
	binary )
	  echo "+ Build regular binary...";
		bash $COLUMBO_HOME/scripts/build-lnx.sh onedir;
		chmod +x "$COLUMBO_BIN";
		ln -s "$COLUMBO_BIN" /usr/local/bin/columbo;
	;;
	standalone )
		bash $COLUMBO_HOME/scripts/build-lnx.sh onefile;
		chmod +x "$COLUMBO_BIN";
		ln -s "$COLUMBO_BIN" /usr/local/bin/columbo;
	;;
esac
