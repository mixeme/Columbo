FROM debian:bullseye

RUN apt update -y && apt install -y git python3 python3-pip python3-pyqt5
RUN python3 -m pip install pyinstaller

# https://github.com/jozo/docker-pyqt5/blob/master/default/Dockerfile
# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

RUN apt install -y qt5dxcb-plugin
RUN apt install -y libx11-xcb1

RUN mkdir /project
WORKDIR /project

CMD ["/bin/bash", "/project/scripts/build-lnx.sh", "onedir"]

# Image build
# docker build --build-arg="PYTHON_VERSION=3.9" --tag mixeme/columbo-build:py3.9 scripts/docker
#
# Build binary
# docker run --user $(id -u):$(id -g) -it --rm --name columbo-build -v $PWD:/project -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro -v /etc/shadow:/etc/shadow:ro mixeme/columbo-build
#
# Run binary
# docker run --user $(id -u):$(id -g) -it --rm --name columbo-build -v $PWD:/project -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro -v /etc/shadow:/etc/shadow:ro -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mixeme/columbo-build dist/columbo-aarch64/columbo-aarch64
#
# Run source
# docker run --user $(id -u):$(id -g) -it --rm --name columbo-build -v $PWD:/project -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro -v /etc/shadow:/etc/shadow:ro -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mixeme/columbo-build:py3.9 python3 main.py
#
# docker build --tag mixeme/columbo-build:deb scripts/docker
# docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mixeme/columbo-build:deb
#
#
#


