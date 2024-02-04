#!/usr/bin/env bash

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ..;
echo "Project home: $PWD";

# Define variables
MANIFEST=$PWD/scripts/flatpak/ru.mixeme.Columbo.yaml;
BUNDLE=$PWD/dist/columbo.flatpak;
BUILD_DIR=~/.cache/columbo;
echo "Manifest: $MANIFEST";


echo "
Select what to do:
  [1] Build & install
  [2] Run
  [3] Export bundle
";

read -p "Select option: " DO_OPTION;

case $DO_OPTION in
	1 )
		# Switch folder
		echo "+ Switch to Flatpak work directory: $BUILD_DIR";
		cd "$BUILD_DIR" || exit 1;

		# Build & install
		echo "+ Build & install";
		flatpak-builder --user --install --force-clean build-dir "$MANIFEST"
	;;
	2 )
		# Run app
		flatpak run ru.mixeme.Columbo;
	;;
	3 )
		# Switch folder
		echo "+ Switch to Flatpak work directory: $BUILD_DIR";
		cd "$BUILD_DIR" || exit 1;

		# Export to the local repo
		flatpak build-export repo build-dir
		
		# Create single-file bundles
		flatpak build-bundle -v repo $BUNDLE ru.mixeme.Columbo --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
	;;
	4 )
		if [ -d $BUILD_DIR ];
			echo "+ Clean $BUILD_DIR";
			rm -R $BUILD_DIR;
		then
			echo "No folder $BUILD_DIR";
		fi
	;;
	* )
		exit 1;
	;;
esac

# Debug app
# # flatpak run --command="bash" ru.mixeme.Columbo
