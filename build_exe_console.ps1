param(
    [string]$Python = "python",
    [string]$Name = "FileServerConsole"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

& $Python -m pip install -r requirements.txt

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --name $Name `
    --add-data "templates;templates" `
    --add-data "config.yaml;." `
    main.py
