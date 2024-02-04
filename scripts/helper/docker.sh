#!/usr/bin/env bash

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
	3 )
		OPTION_IMAGE=$1;
		OPTION_COMMAND=$2;
		OPTION_OTHER=$3;
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
  [1] Debian 11 (reference)
  [2] Debian 10 (legacy)
  [3] CentOS 7  (legacy)
"
	read -p "Select image. Enter [1-3]: " OPTION_IMAGE;
fi

# Ask command option if it is not provided
if [ ! -v OPTION_COMMAND ];
then
	echo "Available commands:
  [0] build base image
  [1] build main image
  [2] pull main image
  [3] run application
  [4] build binary
  [5] push image(s)
  [6] remove image
"
	read -p "Select command. Enter [0-6]: " OPTION_COMMAND;
fi

# Resolve image option
IMAGE_BASENAME="mixeme/columbo";
case $OPTION_IMAGE in
	1 | deb11 )
		BASE_IMAGE="";
		IMAGE_NAME="$IMAGE_BASENAME:debian-bullseye-$ARCH";
		DOCKERFILE=Dockerfile-deb11;
		TAG=${TAG:-"deb11"};
	;;
	2 | deb10 )
		BASE_IMAGE="";
		IMAGE_NAME="$IMAGE_BASENAME:debian-buster-$ARCH";
		DOCKERFILE=Dockerfile-deb10;
		TAG=${TAG:-"deb10"};
	;;
	3 | centos7 )
		BASE_IMAGE="$IMAGE_BASENAME:centos-7-python ";
		IMAGE_NAME="$IMAGE_BASENAME:centos-7-$ARCH";
		DOCKERFILE=Dockerfile-centos7;
		TAG=${TAG:-"centos7"};
	;;
	* )
		echo "Unknown image option. Exit";
		exit 1;
	;;
esac

find_image() {
	IMAGES=$(docker image ls -q $IMAGE_NAME);	# Check image
	if [ -z "$IMAGES" ];
	then
		exit 1;		# No images found
	else
		exit 0;		# Images found
	fi
}

echo "Docker image: $IMAGE_NAME";

# Resolve command option
case $OPTION_COMMAND in
	0 | base )
	;;
	1 | main )
		# Build main Docker image
		echo "+ Build main Docker image: $IMAGE_NAME";
		docker build \
			--tag $IMAGE_NAME \
			--file scripts/docker/$DOCKERFILE \
			scripts/docker > scripts/docker/$TAG.log
	;;
	2 | pull )
		echo "+ Pull main Docker image: $IMAGE_NAME";
		docker pull $IMAGE_NAME
	;;
	3 | run )
		# Check image
		[ ! find_image ] && echo "  No image found. Exit" && exit 1;

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
			"$IMAGE_NAME" \
			python3 src/main.py
	;;
	4 | binary )
		# Check image
		[ ! find_image ] && echo "  No image found. Exit" && exit 1;
		
		echo "+ Build binary";
		echo "Build tag: $TAG";
		docker run \
			--user "$(id -u)":"$(id -g)" \
			-it --rm \
			-v $PWD:/project \
			-v /etc/passwd:/etc/passwd:ro \
			-v /etc/group:/etc/group:ro \
			-v /etc/shadow:/etc/shadow:ro \
			-e TAG=$TAG \
			"$IMAGE_NAME"
	;;
	5 | push )
		# Check image
		[ ! find_image ] && echo "  No image found. Exit" && exit 1;
		
		if [ ! -z $BASE_IMAGE ];
		then
			echo "+ Push base image $BASE_IMAGE";
			docker push "$BASE_IMAGE";
		fi
		
		echo "+ Push main image $IMAGE_NAME";
		docker push "$IMAGE_NAME";
	;;
	6 | remove )
		# Check image
		[ ! find_image ] && echo "  No image found. Exit" && exit 1;
		
		if [ ! -z $BASE_IMAGE ];
		then
			echo "+ Remove base image $BASE_IMAGE";
			docker image rm "$BASE_IMAGE";
		fi
		
		echo "+ Remove main image $IMAGE_NAME";
		docker image rm "$IMAGE_NAME";
	;;
	* )
		exit 2;
esac

# Provide clean exit code
echo "All done!";
exit 0;

