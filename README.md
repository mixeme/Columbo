# Columbo
## Definition
Columbo is an observer of a syncronization/backup (futher just "sync") history. Such a history is produced by sync applications like rsync, rclone, GoodSync, etc.

## What is the problem?
Sync applications collect the history of changes (deleted, overwritten or, sometimes, moved files) in some folder (further a "history folder") in one of 2 ways: **unified** or **by date**.

**Unified (tree)** way means that each sync keeps changes in the history folder. Each changed file is marked with a timestamp suffix in its filename.

**By date** way means that each sync keeps changes in a separate folder inside the history folder. Each folder is marked with a timestamp in its folder name.

Both ways are reasonable, and sometimes it is needed to switch from one view to another. However, changes should be stored in the only one way.

## What does Columbo provide?
Columbo aims to provide a convinient graphical interface to investigate the syncronization history regardless of which a way has been used for the storage and which a way you currently prefer for investigation.

## Technology stack
+ Python 3
+ PyQt 5