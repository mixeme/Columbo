#!/usr/bin/env bash

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ..;
echo "Project home: $PWD";

# Get a platform architecture
ARCH=$(uname -m);
BIN_NAME="columbo-$ARCH";
echo "Detected platform architecture: $ARCH";

# Resolve a number of arguments
case $# in
	0 )
	;;
	1 )
		OPTION_IMAGE=$1;
	;;
	2 )
		OPTION_IMAGE=$1;
		OPTION_COMMAND=$2;
	;;
	3 )
		OPTION_IMAGE=$1;
		OPTION_COMMAND=$2;
		OPTIONS=$3;
	;;
	* )
		exit 1;
	;;
esac

# Ask image option if it is not provided
if ! [ -v OPTION_IMAGE ];
then
	echo "Available images:
	[1] Debian 11 (reference)
	[2] Debian 10 (legacy)
	[3] CentOS 7  (legacy)
	"
	read -p "Select image. Enter number of an option: " OPTION_IMAGE;
fi

# Ask command option if it is not provided
if ! [ -v OPTION_COMMAND ];
then
	echo "Available commands:
	[1] (re)build image
	[2] test run
	[3] build binary
	[4] push image
	"
	read -p "Select command. Enter number of an option: " OPTION_COMMAND;
fi

# Resolve image option
IMAGE_BASENAME="mixeme/columbo";
case $OPTION_IMAGE in
	1 | deb11 )
		IMAGE_NAME="$IMAGE_BASENAME:debian-bullseye-$ARCH";
		DOCKERFILE=Dockerfile-deb11;
		TAG=${TAG:-"deb11"};
	;;
	2 | deb10 )
		IMAGE_NAME="$IMAGE_BASENAME:debian-buster-$ARCH";
		DOCKERFILE=Dockerfile-deb10;
		TAG=${TAG:-"deb10"};
	;;
	3 | centos7 )
		IMAGE_NAME="$IMAGE_BASENAME:centos-7-$ARCH";
		DOCKERFILE=Dockerfile-centos7;
		TAG=${TAG:-"centos7"};
	;;
	* )
		echo "Unknown image option. Exit";
		exit 1;
	;;
esac

# Resolve command option
case $OPTION_COMMAND in
	1 | image )
		BUILD_IMAGE=1;
	;;
	2 | test )
		TEST_RUN=1;
	;;
	3 | binary )
		BUILD_BINARY=1;
	;;
	4 | push )
		BUILD_IMAGE=1;
		PUSH_IMAGE=1;
	;;
	remove )
		REMOVE_IMAGE=1;
	;;
	* )
		exit 2;
esac

case $OPTIONS in
	force )
		BUILD_IMAGE=1;
	;;
esac

echo "Docker image: $IMAGE_NAME";
echo "Tag for binary build: $TAG";
[ -v BUILD_IMAGE ]  && echo "Request to (re)build Docker image";
[ -v TEST_RUN ]     && echo "Request to make a test run";
[ -v BUILD_BINARY ] && echo "Request to build binary";
[ -v PUSH_IMAGE ]   && echo "Request to push Docker image";

# Build Docker image
IMAGES=$(docker image ls -q $IMAGE_NAME);		# Check image
([ -z "$IMAGES" ] && echo "  No image found") || echo "  Found image(s): $IMAGES";
if [ -z "$IMAGES" ] || [ -v BUILD_IMAGE ];
then
	echo "+ (Re)build Docker image: $IMAGE_NAME";
	docker build \
			--tag $IMAGE_NAME \
			--file scripts/docker/$DOCKERFILE \
			scripts/docker > scripts/dockder/$IMAGE_NAME.log
fi

if [ -v TEST_RUN ];
then
	echo "+ Test run...";
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

if [ -v BUILD_BINARY ];
then
	echo "+ Build binary..";
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

if [ -v PUSH_IMAGE ];
then
	echo "+ Push image...";
	docker push $IMAGE_NAME;
fi

if [ -v REMOVE_IMAGE ] && ! [ -z "$IMAGES" ];
then
	docker image rm "$IMAGES";
fi

echo "All done!";
exit 0;

