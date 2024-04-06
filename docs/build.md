# Run / Build
## Run from source
### Windows
1. Install CPython interpreter **(required 3.9+ version)** from
> https://www.python.org/downloads/windows/
2. Open PowerShell (as administrator if you what to install packages for all users, otherwise only for current user);
3. Install `pip`
```shell
py -m ensurepip --upgrade
```
4. Upgrade `pip` to the latest version
```shell
py -m pip install --upgrade pip
```
5. Install `PyQt5` package with `pip`
```shell
py -m pip install PyQt5
```
6. Clone or [download as ZIP](http://github.com/mixeme/Columbo/zipball/main/) Columbo repository;
7. Unpack ZIP (if it is needed);
8. Run Columbo with
```shell
py <path-to-the-unpacked-repo>/main.py
```

### Linux
CPython 3.9+ is required.
```shell
# CentOs 7 & Debain 10 Buster does not have Python 3.9+ in its repo. See instructions for Docker image below

# Debian 11 Bullseye example
apt update -y && apt install -y git python3 python3-pip python3-pyqt5
git clone -b main https://github.com/mixeme/Columbo.git
python3 Columbo/main.py
```

## Build binary
### Natively
1. Check that you can successfully run Columbo from the source. See instructions in the section above;
2. Install [PyInstaller](https://pyinstaller.org/) with `pip`
```shell
py -m pip install pyinstaller         # For Windows  
python3 -m pip install pyinstaller    # For Linux
```
3. Run `scripts/build-win.bat` for Windows and `scripts/build-lnx.sh` for Linux;
4. Find your binary in `dist` folder.

### Another distribution
If you need to run Columbo in another environment than compiled binaries, prepare your own with Docker. You can use our build flow as an example.

### Docker-based build flow
1. [Install](https://docs.docker.com/engine/install/) Docker engine;
2. Clone Columbo repository
```shell
git clone -b main https://github.com/mixeme/Columbo.git
cd Columbo
```
3. Run helper script `scripts/helper/docker.sh`. This script relies on the set of the prepared images (available on [Docker Hub](https://hub.docker.com/r/mixeme/columbo)). You can inspect images through
> `scripts/docker/Dockerfile-deb11`          (Debian 11 Bullseye);
> `scripts/docker/Dockerfile-deb10`          (Debian 10 Buster);
> `scripts/docker/Dockerfile-centos7`        (CentOS 7);
> `scripts/docker/Dockerfile-centos7-python` (CentOS 7 with CPython 3.9+, auxiliary image for the one above);

### Flatpak-based build flow
1. [Install](https://flatpak.org/setup/) `flatpak` and `flatpak-builder`;
2. Clone Columbo repository
```shell
git clone -b main https://github.com/mixeme/Columbo.git
cd Columbo
```
3. Run helper script `scripts/helper/flatpak.sh`. This script relies on the `scripts/flatpak/ru.mixeme.Columbo.yaml` description.

