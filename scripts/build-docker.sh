#!/usr/bin/env bash

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ..;
echo "Project home: $PWD";

# Get a platform architecture
ARCH=$(uname -m);
BIN_NAME="columbo-$ARCH";
echo "Detected platform architecture: $ARCH";

echo "Available images:
[1] Debian 11 (reference)
[2] Debian 10 (legacy)
[3] CentOS 7  (legacy)
"
read -p "Select image. Enter number of an option: " ANS;

IMAGE_BASENAME="mixeme/columbo";
case $ANS in
	1 )
		IMAGE_NAME="$IMAGE_BASENAME:debian-bullseye-$ARCH";
		DOCKERFILE=Dockerfile-deb11;
		TAG=${TAG:-"deb11"};
	;;
	2 )
		IMAGE_NAME="$IMAGE_BASENAME:debian-buster-$ARCH";
		DOCKERFILE=Dockerfile-deb10;
		TAG=${TAG:-"deb10"};
	;;
	3 )
		IMAGE_NAME="$IMAGE_BASENAME:centos-7-$ARCH";
		DOCKERFILE=Dockerfile-centos7;
		TAG=${TAG:-"centos7"};
	;;
	* )
		exit 1;
	;;
esac

IMAGES=$(docker image ls -q);		# Check image
if [ -z $IMAGES ] || [ -v IMAGE_REBUILD ];
then
	docker build --tag $IMAGE_NAME --file docker/$DOCKERFILE docker
fi

if [ -v TEST ];
then
	docker run \
			-it --rm \
			--name columbo-env \
			--user $(id -u):$(id -g) \
			-v $PWD:/project \
			-v /etc/passwd:/etc/passwd:ro \
			-v /etc/group:/etc/group:ro \
			-v /etc/shadow:/etc/shadow:ro \
			-e DISPLAY=$DISPLAY \
			-v /tmp/.X11-unix:/tmp/.X11-unix \
			$IMAGE_NAME \
			python3 main.py
fi

if [ -v BUILD ];
then
	docker run \
			--user $(id -u):$(id -g) \
			-it --rm \
			-v $PWD:/project \
			-v /etc/passwd:/etc/passwd:ro \
			-v /etc/group:/etc/group:ro \
			-v /etc/shadow:/etc/shadow:ro \
			-e TAG=$TAG \
			$IMAGE_NAME
fi

exit 0;

