param(
    [switch]$SkipStartup
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$launcher = Join-Path $root "scripts\start_nova_gui.bat"
$icon = Join-Path $root "assets\nova.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$startup = [Environment]::GetFolderPath("Startup")
$shell = New-Object -ComObject WScript.Shell

function New-NovaShortcut([string]$path, [bool]$runOnStartup) {
    $shortcut = $shell.CreateShortcut($path)
    $shortcut.TargetPath = $launcher
    $shortcut.WorkingDirectory = $root
    $shortcut.IconLocation = "$icon,0"
    $shortcut.Description = if ($runOnStartup) { "Start Nova when you sign in" } else { "Open Nova" }
    $shortcut.Save()
}

New-NovaShortcut (Join-Path $desktop "Nova.lnk") $false
if (-not $SkipStartup) {
    New-NovaShortcut (Join-Path $startup "Nova.lnk") $true
}

Write-Host "Nova launcher created on your Desktop."
if (-not $SkipStartup) { Write-Host "Nova will also start when you sign in." }
