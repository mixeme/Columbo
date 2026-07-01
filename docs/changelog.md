# Changelog

## v0.10.5 - 2026-07-01

### Added

- Added GitHub Actions workflow for executable builds.

### Changed

- Updated project metadata in `pyproject.toml`.
- Bumped project version from `v0.10.4` to `v0.10.5`.

## v0.10.4 - 2026-04-16

### Added

- Added `pyproject.toml` draft for Python package builds.
- Added `src/version` for build-time version metadata.
- Added versioned executable names for Windows and Linux PyInstaller builds.
- Added `scripts/helper/build-all.sh` to run Docker and Flatpak build flows.
- Added asynchronous restore worker for file and directory restoration.
- Added application version to the main window title.
- Added README screenshot image.

### Changed

- Updated README wording and build instruction links.
- Updated build scripts to include `src/version` in packaged artifacts.
- Updated Docker and Flatpak helper scripts for multi-target build flows.
- Moved restore copy work out of the UI action path and into a worker.

### Fixed

- Fixed README typo.
- Fixed file tree loader list reuse between runs.
- Fixed tree action dispatch so the requested worker is started.

## v0.10.1 - 2026-03-06

### Changed

- Updated build documentation links, examples, and Docker/Flatpak build flow descriptions.
- Updated Docker helper image registry from `git.mxme.ru` to `gitea.mixdep.ru`.

## v0.10 - 2026-03-06

### Added

- Added explicit file tree loading before building views.
- Added custom timestamp delimiter support.
- Added directory restore support.
- Added `Set as subpath` action for filtering by selected folder.
- Added reusable path gathering and relative path resolution helpers.
- Added separate workers for file tree building, deletion, and loading.

### Changed

- Split the former monolithic file tree worker into focused builder, loader, and deleter workers.
- Reworked the UI around load, build, filter, delete, expand, collapse, and restore actions.
- Replaced tuple-based view direction handling with `ViewDirection`.
- Renamed `src/core/tree.py` to `src/core/data_model.py`.
- Renamed clear operations to delete operations in `OperationType`.

### Fixed

- Preserved Qt runnable lifetime with a reusable runnable wrapper.
- Rebuilt path handling for conversions between unified and by-date history views.

## v0.9.4 - 2025-05-12

### Added

- Added cross-platform file opening helper.
- Added snapshot timestamp utilities and snapshot validators.
- Added worker support for building, filtering, and deleting file tree data.
- Added sub-path filtering for by-date history views.
- Added context menu actions for opening containing folders and setting filter bounds from selected nodes.

### Changed

- Reworked file tree building around normalized path parts.
- Moved node creation and traversal helpers into `src/core/node.py`.
- Replaced the previous `nodes.py` and `workers.py` modules with more focused modules.

## v0.9.3 - 2024-09-15

### Added

- Added file and folder context menu actions for setting snapshot filter bounds.
- Added `Open in folder` action for files.

### Changed

- Updated Windows build script to package icons from `resources/icons`.
- Updated Flatpak setup to add Flathub as a user remote.

### Fixed

- Fixed selected path reconstruction for context menu actions.

## v0.9.2+ - 2024-04-06

### Changed

- Simplified build documentation.
- Updated Docker helper script with an additional required package.
- Updated README link to build instructions.

## v0.9.2 - 2024-02-13

### Added

- Added `docs/build.md` with source, native, Docker, and Flatpak build instructions.
- Added Docker and Flatpak helper scripts.
- Added Flatpak manifest using `.yaml` extension.
- Added `src/gui/__init__.py`.

### Changed

- Moved application code into the `src/` layout.
- Moved icons into `resources/icons`.
- Moved detailed build instructions out of README and into `docs/build.md`.
- Updated Linux and Windows build scripts for the new project layout.

### Removed

- Removed obsolete `scripts/build-docker.sh`, `scripts/release.sh`, and `.yml` Flatpak manifest paths.

## v0.9.1 - 2024-02-03

### Added

- Added Docker-based build flow and Dockerfiles for Debian 10, Debian 11, CentOS 7, and CentOS 7 with CPython.
- Added Flatpak build flow.
- Added installation helper for Docker.
- Added shared shell helper script for build tooling.
- Added `TreeType` enum for history view modes.

### Changed

- Expanded README with source, binary, Docker, and Flatpak build instructions.
- Updated Linux build script and Docker image handling.
- Updated UI and tree handling code for source and target history view modes.

## v0.9 - 2024-01-21

### Added

- Added initial PyQt graphical interface for browsing synchronization history.
- Added support for unified and by-date history tree views.
- Added file tree nodes with name, last modified, and snapshot columns.
- Added icons for files, folders, and search.
- Added Windows and Linux PyInstaller build scripts.
- Added installation helper scripts for Git and wget.
- Added README with project definition, history layouts, and usage overview.

### Changed

- Updated the GUI and main entrypoint during the initial release preparation.
