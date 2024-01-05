# Columbo
## Definition
Columbo is an observer of a syncronization/backup (futher just "sync") history. Such a history is produced by sync applications like rsync, rclone, GoodSync, etc.

## What is the problem?
Sync applications collect the history of changes (deleted, overwritten or, sometimes, moved files) in some folder (futher "history folder") in one of 2 ways: unified or by date.
*Unified (tree)* way means that file tree in history folder repeats original file tree, and each changed file is marked with a timestamp suffix in its filename.
*By date* way means that each sync provides a snapshot idetified by timestamp. Each snapshot has own history folder, and all changes are stored this folder.
Both ways are reasonable. However, changes should be stored in only the one way.

## What does Columbo provide?
Columbo aims to provide a convinient graphical interface to investigate the syncronization history regardless of which way has been used for storage and which way you prefer for investigation.

## Technology stack
+ Python 3
+ PyQt 5