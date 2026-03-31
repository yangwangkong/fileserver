# FileServer v1.1.0

## Highlights

- Added LibreOffice-first Office preview with PDF rendering for better layout fidelity
- Added compatibility preview and conversion flow for `DOC`, `XLS`, and `PPT`
- Improved fallback preview rendering for Word, Excel, and PowerPoint files
- Bundled LibreOffice runtime into the Windows build output for packaged deployments

## Included improvements

- Office files now try LibreOffice-to-PDF conversion first
- Packaged builds include `dist\LibreOffice` next to `dist\FileServer.exe`
- Preview UI now clearly indicates when LibreOffice PDF preview is being used
- Older Office formats can be converted before previewing

## Upgrade notes

- When distributing the packaged app, keep the full `dist` directory instead of copying only `FileServer.exe`
- `dist\LibreOffice` must remain next to `dist\FileServer.exe`

## Suggested release assets

- `dist\FileServer.exe`
- `dist\LibreOffice\` packaged as a zip, such as `FileServer-v1.1.0-win64-with-libreoffice.zip`
