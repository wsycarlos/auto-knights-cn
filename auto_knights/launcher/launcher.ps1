$WorkspaceFolder = $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
$env:PYTHONIOENCODING = ""
Start-Transcript "$WorkspaceFolder\launcher.log"

$ErrorActionPreference = "Stop"
Set-Location $WorkspaceFolder
[System.Environment]::CurrentDirectory = $WorkspaceFolder


try {
    $version = & git.exe describe --dirty --always 
}
catch {
}
if (-not $version) {
    $version = Get-Content "$WorkspaceFolder\version"
}

$host.ui.RawUI.WindowTitle = "auto-knights: $version"


Add-Type –AssemblyName PresentationFramework

[System.Windows.Window]$mainWindow = [Windows.Markup.XamlReader]::Load( (New-Object System.Xml.XmlNodeReader ([xml](Get-Content "$PSScriptRoot\launcher.xaml"))) )

Add-Type -Language CSharp ([string](Get-Content "$PSScriptRoot\launcher.cs"))

$data = New-Object wsycarlos.AutoKnights.DataContext -Property @{
    DefaultPythonExecutablePath      = . {
        try {
            & py.exe -c 'import sys; print(sys.executable)'
        }
        catch {
            
        }
    }
}
$mainWindow.DataContext = $data

$mainWindow.Content.FindName('startButton').add_Click( 
    {
        $mainWindow.DialogResult = $true
        $mainWindow.Close()
    }
)

$mainWindow.Content.FindName('choosePythonExecutablePathButton').add_Click( 
    {
        $dialog = New-Object Microsoft.Win32.OpenFileDialog -Property @{
            Title            = "Choose python executable"
            Filter           = "Executable|*.exe|Any file|*.*"
            FileName         = $data.PythonExecutablePath
            InitialDirectory = . {
                try {
                    Split-Path $data.PythonExecutablePath -Parent
                }
                catch {
                }
            }
        }
        if ($dialog.ShowDialog()) {
            $data.PythonExecutablePath = $dialog.FileName
        }
    }
)

$mainWindow.Content.FindName('selectPluginButton').add_Click( 
    {
        $env:AUTO_KNIGHTS_PLUGINS = $data.Plugins
        & $data.PythonExecutablePath "$PSScriptRoot\select_plugin.py" | ForEach-Object {
            Write-Host $_
            if ($_.StartsWith("AUTO_KNIGHTS_PLUGINS=")) {
                $data.Plugins = $_.Substring(21)
            }
        }
    }
)


if (-not $mainWindow.ShowDialog()) {
    "Cancelled"
    Exit 0
}

$data | Format-List -Property (
    "Job",
    "Debug", 
    "CheckUpdate",
    "PythonExecutablePath",
    "Plugins",
    "ADBAddress",
    @{
        Name       = "Version"
        Expression = { $version }
    }, 
    @{
        Name       = "Python Version"
        Expression = { & "$($Data.PythonExecutablePath)" -VV }
    }
)

if ($data.Debug) {   
    $env:DEBUG = "auto_knights"
    $env:AUTO_KNIGHTS_LAST_SCREENSHOT_SAVE_PATH = "debug/last_screenshot.png"
    & "$WorkspaceFolder/auto_knights/launcher/rotate_debug_data.ps1"
}

if ($data.CheckUpdate) {
    $env:AUTO_KNIGHTS_CHECK_UPDATE = "true"
}

$env:AUTO_KNIGHTS_PLUGINS = $data.Plugins
$env:AUTO_KNIGHTS_ADB_ADDRESS = $data.ADBAddress

$requireAdmin = (-not $data.ADBAddress)

$verb = "open"
if ($requireAdmin) {
    $verb = "runAs"
}

$command = @"
title auto-knights: $version
cd /d "$WorkspaceFolder"
set "DEBUG=$($env:DEBUG)"
set "AUTO_KNIGHTS_ADB_ADDRESS=$($env:AUTO_KNIGHTS_ADB_ADDRESS)"
set "AUTO_KNIGHTS_CHECK_UPDATE=$($env:AUTO_KNIGHTS_CHECK_UPDATE)"
set "AUTO_KNIGHTS_LAST_SCREENSHOT_SAVE_PATH=$($env:AUTO_KNIGHTS_LAST_SCREENSHOT_SAVE_PATH)"
set "AUTO_KNIGHTS_PLUGINS=$($env:AUTO_KNIGHTS_PLUGINS)"
"$($Data.PythonExecutablePath)" -m auto_knights $($data.Job)
start "auto-knights launcher" cmd.exe /c .\launcher.cmd
exit
"@

"command: "
$command
""
Start-Process cmd.exe -Verb $verb -ArgumentList @(
    "/K",
    ($command -split "`n" -join " && ")
)


if ($data.Debug) {
    Remove-Item -Recurse -Force trash.local

    "Installed packages: "
    
    & cmd.exe /c "`"$($Data.PythonExecutablePath)`" -m pip list 2>&1" | Select-String (
        '^pywin32\b', 
        '^opencv-python\b',
        '^opencv-contrib-python\b',
        '^cast-unknown\b',
        '^numpy\b',
        '^Pillow\b',
        '^mouse\b',
        '^adb-shell\b',
        '^easyocr\b',
        '^zhconv\b',
        '^thefuzz\b',
        '^python-levenshtein\b',
        '^PySimpleGUI\b'
    )
    ""
}


Stop-Transcript
