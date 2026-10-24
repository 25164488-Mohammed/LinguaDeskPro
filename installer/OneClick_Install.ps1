# ============================================================================
# LinguaDesk Pro v6.2 — One-Click Windows 10/11 Native Installer
# عمل المهندس محمد البكير (Mohammed Albukeer — mohammedalbukeer@gmail.com)
# ============================================================================
$ErrorActionPreference = "SilentlyContinue"
$SourceRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $SourceRoot "ui\index.html"))) {
    $SourceRoot = $PSScriptRoot
}
$InstallDir = Join-Path $env:LOCALAPPDATA "LinguaDeskPro"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Path (Join-Path $SourceRoot "*") -Destination $InstallDir -Recurse -Force

$cscPath = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $cscPath)) {
    $cscPath = "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe"
}
$csFile = Join-Path $InstallDir "src\LinguaDeskPro.Desktop\LinguaDeskPro_DesktopHost.cs"
$hostExe = Join-Path $InstallDir "LinguaDeskPro.exe"
if (Test-Path $hostExe) { Remove-Item $hostExe -Force }
if ((Test-Path $cscPath) -and (Test-Path $csFile)) {
    & $cscPath /nologo /target:winexe /out:"$hostExe" /r:System.dll /r:System.Drawing.dll /r:System.Windows.Forms.dll "$csFile" | Out-Null
}

$shortcutScript = Join-Path $InstallDir "scripts\create_shortcuts.ps1"
if (Test-Path $shortcutScript) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $shortcutScript -InstallDir $InstallDir
}

if (Test-Path $hostExe) {
    Start-Process -FilePath $hostExe -WorkingDirectory $InstallDir
} else {
    Start-Process -FilePath "wscript.exe" -ArgumentList "`"$(Join-Path $InstallDir 'Launch_LinguaDeskPro.vbs')`"" -WorkingDirectory $InstallDir
}
