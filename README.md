# FileServer

FileServer is a lightweight internal file management service built with FastAPI. It provides a browser-based file explorer, runtime mount management, password management, and a Windows desktop packaging flow with tray support.

## Highlights

- Web-based file browsing for multiple local or network-mounted directories
- File preview support for images, audio, video, PDF, and text files
- Upload and delete support for writable mounts
- Runtime mount management from the admin page without editing `config.yaml`
- Admin password change from the web UI
- Passwords stored as hashes in runtime config
- Windows EXE packaging with auto-open browser behavior
- System tray mode for background operation

## Screens and Capabilities

The application is designed for local network or personal workstation scenarios where you want a simple file portal without deploying a large storage platform.

Core capabilities:

- login-protected file management
- read-only and writable mount separation
- safe path resolution under configured mount roots
- runtime config override via `runtime_config.yaml`
- tray-based background service for the packaged Windows app

## Project Structure

```text
fileserver/
|-- main.py
|-- config.py
|-- config.yaml
|-- requirements.txt
|-- build_exe.ps1
|-- routers/
|   |-- auth.py
|   |-- files.py
|   `-- admin.py
`-- templates/
    |-- base.html
    |-- index.html
    |-- login.html
    |-- preview.html
    `-- settings.html
```

## Configuration Model

`config.yaml` is the base configuration file.

At runtime, FileServer writes mutable settings into `runtime_config.yaml`, including:

- mount definitions
- password hash

This allows the app to keep source-controlled defaults separate from runtime-only settings changed in the admin UI.

## Run From Source

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the server:

```powershell
python main.py
```

Then open:

```text
http://127.0.0.1:8591
```

## Build the Windows EXE

```powershell
.\build_exe.ps1
```

Build output:

```text
dist\FileServer.exe
```

Packaged app behavior:

- starts the FastAPI service in the background
- waits for the local port to become ready
- opens the browser automatically
- stays available from the system tray

## Security Notes

- Passwords changed from the UI are stored with PBKDF2-HMAC-SHA256 hashing
- Runtime-generated passwords are not stored in plain text
- Access is constrained to configured mount roots
- Only mounts marked as writable can upload or delete content

## Recommended Ignore Rules

These files should not be committed:

- `dist/`
- `build/`
- `__pycache__/`
- `runtime_config.yaml`
- `fileserver_runtime.log`
- `*.spec`

## Publishing Notes

This repository intentionally uses placeholder values in example config files. Before using the project in production, replace sample values with your own environment-specific settings.

## License

Add the license you want before publishing publicly.
