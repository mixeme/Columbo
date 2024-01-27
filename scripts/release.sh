#!/usr/bin/env bash

# Switch to scripts location
cd "$(dirname "$0")" || exit 1;
echo "Script's folder: $PWD";

echo "+ Go to dist folder";
cd ../dist


TARS=$(ls -1 *.tar.gz);
echo "$TARS";

# Create archives
FOLDERS=$(ls -1 */);
for i in $FOLDERS;
do
  echo "+ TAR $i";
  tar -czvf $i.tar.gz $i;
done
