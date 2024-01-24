#!/usr/bin/env sh

check_app_bin() {
  if [ -f $SYSTEM_BIN ];
  then
    exit 0;
  else
    exit 1;
  fi
}

check_app_folder() {
  if [ -d $COLUMBO_HOME ];
  then
    exit 0;
  else
    exit 1;
  fi
}

check_previous() {
  check_app_bin && echo "Found an application binary at $SYSTEM_BIN. Delete it" && rm $SYSTEM_BIN;
  check_app_folder && echo "Found an application folder at $COLUMBO_HOME. Delete it" && rm -R $COLUMBO_HOME;
}

build_docker() {
  DOCKER_IMAGE="mixeme/columbo-build:debian-bullseye";

  # Build a Docker image with the required environment
  docker build --tag "${DOCKER_IMAGE}" docker

  # Run a container for building binary
  docker run \
        -it --rm \
        --name columbo-build \
        --user $(id -u):$(id -g) \
        -v ../:/project \
        -v /etc/passwd:/etc/passwd:ro \
        -v /etc/group:/etc/group:ro \
        -v /etc/shadow:/etc/shadow:ro \
        -e MODE=$1 \
        "${DOCKER_IMAGE}"

  # Remove Docker image
  docker image rm "${DOCKER_IMAGE}"
}

build_native() {

}

install_app() {
    # Resolve variables
    COPY_SOURCE="../dist/${BIN_NAME}";
    case $1 in
      onedir )
        COPY_TARGET="${COLUMBO_HOME}";
        COLUMBO_BIN="${COLUMBO_HOME}/${BIN_NAME}";
      ;;
      onefile )
        COPY_TARGET="${SYSTEM_BIN}";
        COLUMBO_BIN="${SYSTEM_BIN}";
      ;;
    esac

    # Copy binary
    echo "+ Copy binary from $COPY_SOURCE to $COPY_TARGET";
    cp -R "$COPY_SOURCE" "$COPY_TARGET";

    # Make binary executable
    echo "+ Make $COLUMBO_BIN executable";
		chmod +x "$COLUMBO_BIN";

    # Create symlink for binary to Columbo home
    RUN_MESSAGE="\t$(basename $SYSTEM_BIN) | $SYSTEM_BIN";
    if [ "$1" = "onedir" ];
    then
      echo "+ Create symlink for $COLUMBO_BIN as $SYSTEM_BIN";
      ln -s "$COLUMBO_BIN" $SYSTEM_BIN;
      RUN_MESSAGE="$RUN_MESSAGE | $COLUMBO_BIN";
    fi

    # Show message for application run
		echo "Run Columbo as";
		echo -e "$RUN_MESSAGE";

		# Clean exit from function
		exit 0;
}