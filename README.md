# Columbo
## Definition
Columbo is an observer of a syncronization/backup (futher just "sync") history. Such a history is produced by sync applications like rsync, rclone, GoodSync, etc.

## What is the problem?
Sync applications collect the history of changes (deleted, overwritten or, sometimes, moved files) in some folder in one of 2 ways: unified or by date.
Unified (tree) way means that file tree in history folder repeats original tree and changed file is marked with tinestamp suffix in its filename.

## What does Columbo provide?
The main motivation is to provide a convinient graphical interface to investigate the syncronization history

## Technology stack
+ Python 3
+ PyQt 5