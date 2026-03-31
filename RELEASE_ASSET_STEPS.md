# GitHub Release Asset Steps

This file explains how to publish `dist\FileServer.exe` as a GitHub Release asset.

## 1. Build the executable

Run:

```powershell
.\build_exe.ps1
```

Expected output:

```text
dist\FileServer.exe
```

## 2. Open the GitHub repository

Repository:

```text
https://github.com/yangwangkong/fileserver
```

## 3. Create a new release

On GitHub:

1. Open the repository page
2. Click `Releases`
3. Click `Draft a new release`

## 4. Fill in release information

Recommended values:

- Tag: `v1.0.0`
- Release title: `FileServer v1.0.0`

You can use the content from:

- [RELEASE_v1.0.0.md](RELEASE_v1.0.0.md)

## 5. Upload the EXE asset

In the release draft page:

1. Find the attachment area
2. Drag and drop:

```text
dist\FileServer.exe
```

3. Wait until the upload completes

## 6. Publish

After confirming the title, tag, release notes, and uploaded asset:

1. Click `Publish release`

## Recommended Release Notes

You can copy this file directly:

- [RELEASE_v1.0.0.md](RELEASE_v1.0.0.md)

## Recommended Checks Before Publishing

- Confirm the EXE is built from the latest code
- Confirm example config files do not contain real credentials
- Confirm `runtime_config.yaml` is not included
- Confirm the EXE starts and the local page opens successfully
