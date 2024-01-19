#!/usr/bin/env sh

# wget https://github.com/mixeme/Columbo/raw/dev/scripts/install.sh
# sudo bash [source | binary | standalone]

if [ "$#" -eq 0 ];
then
  COMMAND=source;
  echo "No arguments are provided. Use default option" $COMMAND;
else
  COMMAND=$1;
fi

case $COMMAND in
	source )
	    echo "Columbo will installed as source";
	;;
	binary )
	  echo "Columbo will installed as regular binary";
	;;
	standalone )
	  echo "Columbo will installed as standalone binary";
	;;
	* )
	echo "Unknown command ${COMMAND}";
	echo "Possible commands: source (default) | binary | standalone";
esac

cd $(dirname $0);

BRANCH=dev;
ARCH=$(uname -m);
COLUMBO_HOME=/opt;
COLUMBO_PY="$COLUMBO_HOME/Columbo/main.py";
COLUMBO_BIN="$COLUMBO_HOME/Columbo/columbo-$ARCH";

apt install git python3 python3-pip python3-pyqt5;
pip install --upgrade pyinstaller

# If `pip` command is unknown then
# 	python -m pip install --upgrade pyinstaller

cd "$COLUMBO_HOME";
git clone -b $BRANCH https://github.com/mixeme/Columbo.git;

case $COMMAND in
	source )
		chmod +x $COLUMBO_PY;
		ln -s $COLUMBO_PY /usr/local/bin/columbo;
	;;
	binary )
		bash build-lnx.sh onedir;
		chmod +x "$COLUMBO_BIN";
		ln -s "$COLUMBO_BIN" /usr/local/bin/columbo;
	;;
	standalone )
		bash build-lnx.sh onefile;
		chmod +x "$COLUMBO_BIN";
		ln -s "$COLUMBO_BIN" /usr/local/bin/columbo;
	;;
esac
