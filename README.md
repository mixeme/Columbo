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

## Get binary
In the release section, you can find binaries which are built with [PyInstaller](https://pyinstaller.org/). There are the following binaries:

+ Windows x86_64 (built on Windows 10 22H2);
+ Linux x86_64 (built on CentOS 7 & Debian 10 Buster);
+ Linux ARM64 (built on Debian 11 Bullseye & Debian 10 Buster);
+ Flatpak for x86_64 & ARM64.

If you need another version, you can run Columbo from source or a build binary on your own. See instructions in `docs/build.md`.
