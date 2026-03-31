# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, adapted to the current project history.

## [Unreleased]

- Added LibreOffice-first Office preview with PDF rendering for improved layout fidelity
- Added bundled LibreOffice runtime support in Windows build output
- Added compatibility preview and conversion flow for DOC, XLS, and PPT files
- Improved fallback preview rendering for Word, Excel, and PowerPoint files

## [2026-03-31] Security hardening

### Added

- CSRF protection for login, mount management, password change, upload, and delete operations
- Runtime-generated secure session secret fallback when no strong secret is configured

### Changed

- Restricted login `next` redirects to internal relative paths only
- Increased password change minimum length requirement
- Updated frontend templates to include CSRF tokens in forms and AJAX requests

### Fixed

- Reduced risk of forged session cookies when example or weak secret values are used
- Reduced risk of cross-site request forgery on privileged operations
- Reduced risk of open redirect after login

## [2026-03-31] Documentation and release prep

### Added

- MIT license
- Bilingual README
- Repository metadata notes
- Release notes draft
- GitHub release asset publishing guide

### Changed

- Sanitized sample configuration values to avoid publishing meaningful password or secret examples

## [2026-03-31] Initial release

### Added

- FastAPI-based file server with login protection
- Multi-mount file browsing and preview
- Upload and delete support for writable mounts
- Runtime mount management
- Admin password change support
- Password hash storage in runtime config
- Windows EXE packaging
- Browser auto-open and tray background mode
