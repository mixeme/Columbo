#!/usr/bin/env bash

# Test Docker binary
[ -z $(which docker) ] && echo "No 'docker' binary. Exit" && exit 1;

# Define auxiliarly functions
find_image() {
	IMAGES="$(docker image ls -q $1)";
	if [ -z "$IMAGES" ];
	then
		return 1;	# No images found
	else
		return 0;	# Images found
	fi
}

docker_build_invoke() {
	SUFFIX=$(echo $1 | cut -d ':' -f 2);
	LOG=scripts/docker/log/$SUFFIX.log;
	[ ! -d $(dirname $LOG) ] && mkdir -p $(dirname $LOG);
	echo "+ Build Docker image '$1'. See log file $PWD/$LOG";
	docker build \
		--tag $1 \
		--file scripts/docker/$2 \
		scripts/docker > $LOG;
	echo "+ Build finished";
}

# Change location to the project home
cd "$(dirname "$0")" || exit 1;
cd ../..;
echo "Project home: $PWD";

# Get a platform architecture
ARCH=$(uname -m);
echo "Platform architecture: $ARCH";

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
	* )
		echo "Incorrect number of arguments. Exit";
		exit 1;
	;;
esac

# Ask image option if it is not provided
if [ ! -v OPTION_IMAGE ];
then
	echo "Available images:
  [1] Debian 11 {deb11}   (reference)
  [2] Debian 10 {deb10}   (legacy)
  [3] CentOS 7  {centos7} (legacy)
"
	read -p "Select image. Enter [1-3] or {word}: " OPTION_IMAGE;
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
		BASE_IMAGE="$IMAGE_BASENAME:centos-7-python";
		DOCKERFILE_BASE=Dockerfile-centos7-python;
		
		IMAGE_NAME="$IMAGE_BASENAME:centos-7-$ARCH";
		DOCKERFILE=Dockerfile-centos7;
		TAG=${TAG:-"centos7"};
	;;
	* )
		echo "Unknown image. Exit";
		exit 1;
	;;
esac
echo "Docker image: '$IMAGE_NAME'";

# Ask command option if it is not provided
if [ ! -v OPTION_COMMAND ];
then
	echo "Available commands:
  [0] build {base} image
  [1] build {main} image
  [2] -
  [3] {run} application
  [4] build {binary}
  [5] {push} image(s)
  [6] {remove} image
"
	read -p "Select command. Enter [0-6] or {word}: " OPTION_COMMAND;
fi

# Resolve command option
case $OPTION_COMMAND in
	0 | base )
		# Build base Docker image (with CPython 3.9+)
		if [ -v DOCKERFILE_BASE ] && [ -v BASE_IMAGE ];
		then
#			echo "+ Build base Docker image: $BASE_IMAGE";
#			docker build \
#				--tag $BASE_IMAGE \
#				--file scripts/docker/$DOCKERFILE_BASE \
#				scripts/docker > scripts/docker/$TAG-base.log
#			echo "+ Build finished";
			docker_build_invoke $BASE_IMAGE $DOCKERFILE_BASE;
		else
			[ ! -v DOCKERFILE_BASE ] && echo "Dockerfile for base image is not defined!";
			[ ! -v BASE_IMAGE ]      && echo "Name of base image is not defined!";
		fi
	;;
	1 | main )
		# Build main Docker image
#		echo "+ Build main Docker image: $IMAGE_NAME";
#		docker build \
#			--tag $IMAGE_NAME \
#			--file scripts/docker/$DOCKERFILE \
#			scripts/docker > scripts/docker/$TAG.log
#		echo "+ Build finished";
		docker_build_invoke $IMAGE_NAME $DOCKERFILE;
	;;
	3 | run )
		# Run application
		echo "+ Run application";
		docker run \
			--name columbo-env \
			--user "$(id -u)":"$(id -g)" \
			-it --rm \
			-v $PWD:/project \
			-v /etc/passwd:/etc/passwd:ro \
			-v /etc/group:/etc/group:ro \
			-v /etc/shadow:/etc/shadow:ro \
			-e DISPLAY=$DISPLAY \
			-v /tmp/.X11-unix:/tmp/.X11-unix \
			$IMAGE_NAME \
			python3 src/main.py
	;;
	4 | binary )
		# Build binary
		echo "+ Build binary";
		docker run \
			--user "$(id -u)":"$(id -g)" \
			-it --rm \
			-v $PWD:/project \
			-v /etc/passwd:/etc/passwd:ro \
			-v /etc/group:/etc/group:ro \
			-v /etc/shadow:/etc/shadow:ro \
			-e TAG=$TAG \
			$IMAGE_NAME
	;;
	5 | push )
		# Push images to Docker Hub
		if [ -v BASE_IMAGE ] && find_image $BASE_IMAGE;
		then
			echo "+ Push base image: $BASE_IMAGE";
			docker push $BASE_IMAGE;
		else
			[ -v BASE_IMAGE ] && echo "  No base image found";
		fi
		
		if find_image $IMAGE_NAME;
		then
			echo "+ Push main image: $IMAGE_NAME";
			docker push $IMAGE_NAME;
		else
			echo "  No main image found";
		fi 
	;;
	6 | remove )
		# Remove images
		if find_image $IMAGE_NAME;
		then
			echo "+ Remove main image '$IMAGE_NAME'";
			docker image rm $IMAGE_NAME;
		else
			echo "  No main image found";
		fi
		
		if [ -v BASE_IMAGE ] && find_image $BASE_IMAGE;
		then
			echo "+ Remove base image '$BASE_IMAGE'";
			docker image rm $BASE_IMAGE;
		else
			[ -v BASE_IMAGE ] && echo "  No base image found";
		fi
	;;
	* )
		echo "Unknown command. Exit";
		exit 2;
esac

# Provide clean exit code
exit 0;
