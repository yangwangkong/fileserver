# FileServer v1.0.0

First public release of FileServer.

## Overview

FileServer is a lightweight FastAPI-based file management service with a browser UI and a Windows desktop packaging flow.

## Included in this release

- Multi-mount file browsing
- File preview for common formats
- Upload and delete support for writable mounts
- Runtime mount management from the admin page
- Admin password change support
- Password hash storage in runtime config
- Windows EXE packaging
- Browser auto-open on startup
- System tray background mode

## Notes

- Example config files use placeholder credentials only
- Runtime-generated config is not included in the repository
- Recommended first step after launch: update the admin password from the settings page

## Build Output

Main Windows package:

```text
dist\FileServer.exe
```
