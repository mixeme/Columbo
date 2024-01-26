FROM debian:bullseye

RUN apt update -y \
	&& apt install -y git \
	python3 python3-pip python3-pyqt5 \
	qt5-gtk2-platformtheme qt5-gtk-platformtheme qt5-style-plugins 
RUN python3 -m pip install pyinstaller

# Got from https://github.com/jozo/docker-pyqt5/blob/master/default/Dockerfile
# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

RUN mkdir /project
WORKDIR /project

CMD ["/bin/bash", "/project/scripts/build-lnx.sh", "onedir"]

# Image build
# docker build --tag mixeme/columbo-build:debian-bullseye scripts/docker
#
# Test run from source
# docker run --user $(id -u):$(id -g) -it --rm --name columbo-build -v $PWD:/project -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro -v /etc/shadow:/etc/shadow:ro -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mixeme/columbo-build:debian-bullseye python3 main.py
#
# Build binary
# docker run --user $(id -u):$(id -g) -it --rm --name columbo-build -v $PWD:/project -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro -v /etc/shadow:/etc/shadow:ro mixeme/columbo-build:debian-bullseye
