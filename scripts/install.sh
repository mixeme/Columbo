#!/usr/bin/env sh

# wget https://github.com/mixeme/Columbo/raw/dev/scripts/install.sh
# sudo bash [source | binary | standalone]

if [ "$#" -eq 0 ];
then
  COMMAND=source;
else
  COMMAND=$1;
fi

case $COMMAND in
	source )
	;;
	binary )
	;;
	standalone )
	;;
	* )
	echo "Unknown command ${COMMAND}";
	echo "Possible commands: source (default) | binary | standalone";
esac

cd $(dirname $0)

COLUMBO_HOME=/opt
COLUMBO_PY=Columbo/main.py

apt install git python3 python3-pip python3-pyqt5;
pip install --upgrade pyinstaller

# If `pip` command is unknown then
# 	python -m pip install --upgrade pyinstaller

cd $COLUMBO_HOME;
git clone https://github.com/mixeme/Columbo.git;

case $COMMAND in
	source )
		chmod +x $COLUMBO_PY;
		ln -s $COLUMBO_HOME/$COLUMBO_PY /usr/local/bin/columbo;
	;;
	binary )
		bash build-lnx.sh onedir
	;;
	standalone )
		bash build-lnx.sh onefile
	;;
esac

