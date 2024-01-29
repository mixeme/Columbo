# Columbo
## Definition
Columbo is an observer of a syncronization/backup (futher just "sync") history. Such a history is produced by sync applications like rsync, rclone, GoodSync, etc.

## What is the problem?
Sync applications collect the history of changes (deleted, overwritten or, sometimes, moved files) in some folder (further a "history folder") in one of 2 ways: **unified** or **by date**.

**Unified (tree)** way means that each sync keeps changes directly in the history folder (unified history). Each changed file is marked with a timestamp suffix in its name.

```
history
  ├── Folder 1
  │   └── Folder 3
  │       ├── File 1_2024-01-01_10-00-00
  │       └── File 1_2024-01-02_06-00-00
  └── Folder 2
      └── File 2_2024-01-02_06-00-00
```

**By date (tree)** way means that each sync keeps changes in a separate folder inside the history folder (separated by date history). Each separate folder is marked with a timestamp in its name.

```
history
  ├── 2024-01-01_10-00-00
  │   └── Folder 1
  │       └── Folder 3
  │           └── File 1
  └── 2024-01-02_06-00-00
      ├── Folder 1
      │   └── Folder 3
      │       └── File 1
      └── Folder 2
          └── File 2
```

Both ways are reasonable. For example, the unified way helps to understand what and when has been changed in a certain place. The by date way helps to understand what has been changed at a certain time. So, sometimes it is needed to switch from one view to another. However, the history can be stored in the only one way.

## What does Columbo provide?
Columbo aims to provide a cross-platform convenient graphical interface to investigate the syncronization history regardless of which a way has been used for the storage and which a way you currently prefer for an investigation.

## Technology stack
+ Python 3.9+;
+ PyQt 5.

## Run / Install / Build
### Get binary
In the release section, you can find binaries which are built with [PyInstaller](https://pyinstaller.org/). There are the following binaries:

+ Windows x86_64 (build on Windows 10 22H2);
+ Linux x86_64 (build on CentOS 7);
+ Linux ARM64 (build on Debian Bullseye).

If you need another version, you can run Columbo from source or build binary on your own. See instructions in the corresponding sections below. 

### Run from source
#### Windows
1. Install CPython interpreter **(required 3.9+ version)** from
> https://www.python.org/downloads/windows/
2. Open PowerShell as administrator;
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
6. Clone or [download as ZIP](http://github.com/mixeme/Columbo/zipball/main/) Columbo repo;
7. Unpack ZIP (if it is needed);
8. Run Columbo with
```shell
py <path-to-the-unpacked-repo>/main.py
```

#### Linux
CPython 3.9+ is required.
```shell
# Debian 11 version
apt update -y && apt install -y git python3 python3-pip python3-pyqt5
git clone -b main https://github.com/mixeme/Columbo.git
python3 Columbo/main.py
```

### Build from source
#### Natively
1. Check that you can successfully run Columbo from the source. See instructions in the section above;
2. Install [PyInstaller](https://pyinstaller.org/) with `pip`

```shell
py -m pip install pyinstaller         # For Windows  
python3 -m pip install pyinstaller    # For Linux
```

3. Run `scripts/build-win.bat` for Windows and `scripts/build-lnx.sh` for Linux;
4. Find your binary in `<repo>/dist` folder.

#### With Docker image
1. Install Docker engine;

```shell
apt install docker docker.io apparmor # For example
```

2. Build an image with the required environment 

```shell
# Debian 10 Buster
docker build  --tag mixeme/columbo:debian-buster \
              --file Dockerfile-deb10 \
              https://github.com/mixeme/Columbo.git#dev:scripts/docker

# Debian 10 Bullseye
docker build  --tag mixeme/columbo:debian-bullseye \
              --file Dockerfile-deb11 \
              https://github.com/mixeme/Columbo.git#dev:scripts/docker

# CentOS 7 (x86_64)
docker build  --tag mixeme/columbo:centos-7 \
              --file Dockerfile-centos7-x86_64 \
              https://github.com/mixeme/Columbo.git#dev:scripts/docker
```

3. Clone Columbo repository

```shell
git clone -b main https://github.com/mixeme/Columbo.git
cd Columbo
```

4. Run a container to build a binary

```shell
docker run  --user $(id -u):$(id -g) \
            -it --rm \
            --name columbo-build \
            -v $PWD:/project \
            -v /etc/passwd:/etc/passwd:ro \
            -v /etc/group:/etc/group:ro \
            -v /etc/shadow:/etc/shadow:ro \
            mixeme/columbo:<your-image-version>
```

5. Get your binary in `dist` folder.  

If you need to test compatibility of the built environment, use the following command to run Columbo from the source inside a container

```shell
docker run  --user $(id -u):$(id -g) \
            -it --rm \
            --name columbo-build \
            -v $PWD:/project \
            -v /etc/passwd:/etc/passwd:ro \
            -v /etc/group:/etc/group:ro \
            -v /etc/shadow:/etc/shadow:ro \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -e DISPLAY=$DISPLAY \
            mixeme/columbo:<your-image-version> \
            python3 main.py
            # or `python3.9 main.py` for some images
```

### Install from source
1. Run `scripts/install.sh`. For example
```shell
wget https://github.com/mixeme/Columbo/raw/main/scripts/install.sh \
    && sudo bash [source | regular | standalone]
   
sudo apt install -y git \
    && git clone -b main https://github.com/mixeme/Columbo.git \
    && sudo bash Columbo/scripts/install-git.sh [source | regular | standalone]
```
2. Run Columbo
```shell
    /opt/Columbo/main.py  # for `source` option
    columbo               # for `regular` & `standalone` options 
```



#### Natively


#### With Docker image

### Windows

