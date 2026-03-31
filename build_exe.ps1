param(
    [string]$Python = "python",
    [string]$Name = "FileServer"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

& $Python -m pip install -r requirements.txt

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name $Name `
    --add-data "templates;templates" `
    --add-data "config.yaml;." `
    main.py

Write-Host "Build complete: $projectRoot\dist\$Name.exe"
Write-Host "After first launch, change mount paths or password from the settings page."
