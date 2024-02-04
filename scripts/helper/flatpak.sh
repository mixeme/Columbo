#!/usr/bin/env bash

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ../..;
echo "Project home: $PWD";

# Define variables
APP_ID=ru.mixeme.Columbo;
MANIFEST=$PWD/scripts/flatpak/$APP_ID.yaml;
ARCH=$(uname -m);
BUNDLE=$PWD/dist/columbo-$ARCH.flatpak;
BUILD_DIR=~/.cache/columbo;
echo "Manifest: $MANIFEST";
echo "Platform architecture: $ARCH";

# Resolve action
if [ $# -eq 0 ];
then
	echo "Select action:
  [0] Install dev. tools
  [1] Build & install
  [2] Run application
  [3] Export bundle
  [4] Import bundle
  [5] Clean build dir.
";
	read -p "Select option: " OPTION_ACTION;
else
	OPTION_ACTION=$1;
fi

# Resolve action
case $OPTION_ACTION in
	0 | tools )
		# Test Flatpak binaries
		[ -z $(which flatpak) ] && echo "flatpak is not found. Exit" && exit 1;
		[ -z $(which flatpak-builder) ] && echo "flatpak-builder is not found. Exit" && exit 1;
		
		echo "+ Install development tools";
		#sudo apt install -y flatpak flatpak-builder;
		flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
		flatpak install -y --user \
			org.kde.Platform/$ARCH/5.15-23.08 \
			org.kde.Sdk/$ARCH/5.15-23.08 \
			com.riverbankcomputing.PyQt.BaseApp/$ARCH/5.15-23.08
	;;
	1 | build )
		# Switch folder
		echo "+ Switch to Flatpak work directory: $BUILD_DIR";
		mkdir -p "$BUILD_DIR";
		cd "$BUILD_DIR" || exit 1;
		
		# Build & install
		echo "+ Build & install $APP_ID";
		flatpak-builder --user --install --force-clean build-dir "$MANIFEST"
	;;
	2 | run )
		# Run app
		flatpak run $APP_ID;
	;;
	3 | export )
		# Switch folder
		echo "+ Switch to Flatpak work directory: $BUILD_DIR";
		cd "$BUILD_DIR" || exit 1;

		# Export to the local repo
		echo "+ Export to local repo: $BUILD_DIR/repo";
		flatpak build-export repo build-dir
		
		# Create single-file bundle
		echo "+ Create bundle $BUNDLE";
		flatpak build-bundle repo $BUNDLE $APP_ID --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
	;;
	4 | import )
		flatpak install --user --bundle dist/columbo-$ARCH.flatpak
	;;
	5 | clean )
		if [ -d $BUILD_DIR ];
		then
			echo "+ Clean $BUILD_DIR";
			rm -R -v $BUILD_DIR;
		else
			echo "No folder $BUILD_DIR";
		fi
	;;
	* )
		exit 1;
	;;
esac

# Provide clean exit code
echo "All done!";
exit 0;

# Debug app
# flatpak run --command="bash" ru.mixeme.Columbo
# flatpak uninstall --unused
# flatpak uninstall --all
# flatpak list --columns=application
#
# https://flatpak-testing.readthedocs.io/en/latest/building-simple-apps.html
# https://docs.flatpak.org/en/latest/first-build.html
