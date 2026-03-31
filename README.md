# FileServer

A lightweight internal file management service built with FastAPI, with Windows EXE packaging, tray mode, browser auto-launch, runtime mount management, and password change support.

## Features

- Browse multiple local or network-mounted directories from a web UI
- Preview common file types including images, audio, video, PDF, and text
- Upload and delete files in writable mounts
- Manage mount paths from the admin settings page without editing `config.yaml`
- Change the admin password from the web UI
- Store runtime password as a hash instead of plain text
- Package as a Windows `EXE`
- Launch browser automatically on startup
- Run in the system tray and exit cleanly from the tray menu

## Project Structure

```text
fileserver/
├─ main.py                  # App entrypoint, tray integration, browser auto-open
├─ config.py                # Config loading, runtime config merge, password hashing
├─ config.yaml              # Base config
├─ requirements.txt         # Python dependencies
├─ build_exe.ps1            # Build Windows EXE with PyInstaller
├─ routers/
│  ├─ auth.py               # Login and logout
│  ├─ files.py              # File browse, preview, upload, delete
│  └─ admin.py              # Mount management and password change
└─ templates/               # Jinja2 templates
```

## Runtime Config Behavior

`config.yaml` is treated as the base configuration.

At runtime, the program writes user-managed settings into `runtime_config.yaml`, including:

- mount list
- password hash

This means you can update mounts and password from the admin page without modifying the original `config.yaml`.

## Quick Start

### 1. Install dependencies

```powershell
pip install -r requirements.txt
```

### 2. Run from source

```powershell
python main.py
```

Open:

```text
http://127.0.0.1:8591
```

## Build EXE

```powershell
.\build_exe.ps1
```

Generated file:

```text
dist\FileServer.exe
```

The packaged app:

- starts the FastAPI service in the background
- opens the browser automatically when the local service is ready
- keeps running in the system tray

## Default Login

Base credentials are defined in `config.yaml`.

After the first login, it is recommended to change the password from the settings page. Once changed, the new password is stored in `runtime_config.yaml` as a hash.

## Security Notes

- Passwords changed from the UI are stored as PBKDF2-HMAC-SHA256 hashes
- Path access is restricted to configured mount roots
- Only mounts marked as writable allow upload and delete

## Recommended Git Ignore

Do not commit these runtime or build artifacts:

- `dist/`
- `build/`
- `__pycache__/`
- `runtime_config.yaml`
- `fileserver_runtime.log`
- `*.spec`

## License

Add the license you want before publishing publicly.
