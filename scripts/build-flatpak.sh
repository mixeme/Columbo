#!/usr/bin/env bash

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ..;
echo "Project home: $PWD";

# Define variables
ARCH=$(uname -m);
MANIFEST=$PWD/scripts/flatpak/ru.mixeme.Columbo.yaml;
BUNDLE=$PWD/dist/columbo-$ARCH.flatpak;
BUILD_DIR=~/.cache/columbo;
echo "Manifest: $MANIFEST";

# Ask user
echo "Select what to do:
  [1] Build & install
  [2] Run
  [3] Export bundle
  [4] Clean
";
read -p "Select option: " DO_OPTION;

# Resolve action
case $DO_OPTION in
	1 )
		# Switch folder
		echo "+ Switch to Flatpak work directory: $BUILD_DIR";
		mkdir -p "$BUILD_DIR";
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
		echo "+ Export to local repo: $BUILD_DIR/repo";
		flatpak build-export repo build-dir
		
		# Create single-file bundle
		echo "+ Create bundle $BUNDLE";
		flatpak build-bundle repo $BUNDLE ru.mixeme.Columbo --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
	;;
	4 )
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
exit 0;

# Install deps
# flatpak install -y --user org.kde.Platform/x86_64/5.15-23.08
# flatpak install -y --user org.kde.Sdk/x86_64/5.15-23.08
# flatpak install -y --user com.riverbankcomputing.PyQt.BaseApp/x86_64/5.15-23.08
#
# Debug app
# flatpak run --command="bash" ru.mixeme.Columbo
#
# flatpak install --user --bundle columbo.flatpak
# flatpak uninstall ru.mixeme.Columbo
# flatpak uninstall --unused
#
# flatpak --user remote-add --no-gpg-verify --if-not-exists ru.mixeme.Columbo repo
# flatpak --user install  ru.mixeme.Columbo  ru.mixeme.Columbo

# https://flatpak-testing.readthedocs.io/en/latest/building-simple-apps.html
# https://docs.flatpak.org/en/latest/first-build.html
