#!/usr/bin/env bash

# Switch to scripts location
cd "$(dirname "$0")" || exit 1;
echo "Script's folder: $PWD";

echo "+ Go to dist folder";
cd ../dist


TARS=$(find . -mindepth 1 -maxdepth 1 -type f -name "*tar.gz");
echo "$TARS";

if [ -z "$TARS" ];
then
	echo "No TARS";
fi

# Create archives
FOLDERS=$(find . -mindepth 1 -maxdepth 1 -type d | sed 's|^\./||g');
for i in $FOLDERS;
do
  echo "+ TAR $i";
  tar -czvf $i.tar.gz $i;
done
