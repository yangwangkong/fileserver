param(
    [string]$Python = "python",
    [string]$Name = "FileServer"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$libreOfficeSource = "C:\Program Files\LibreOffice"
$libreOfficeTarget = Join-Path $projectRoot "dist\LibreOffice"
Set-Location $projectRoot

& $Python -m pip install -r requirements.txt

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name $Name `
    --hidden-import win32com.client `
    --hidden-import pythoncom `
    --hidden-import pywintypes `
    --add-data "templates;templates" `
    --add-data "config.yaml;." `
    main.py

if (Test-Path $libreOfficeSource) {
    Write-Host "Bundling LibreOffice runtime..."
    if (Test-Path $libreOfficeTarget) {
        Remove-Item -LiteralPath $libreOfficeTarget -Recurse -Force
    }
    Copy-Item -LiteralPath $libreOfficeSource -Destination $libreOfficeTarget -Recurse
    Write-Host "LibreOffice bundled at: $libreOfficeTarget"
}

Write-Host "Build complete: $projectRoot\dist\$Name.exe"
Write-Host "After first launch, change mount paths or password from the settings page."
