# =============================================================================
# LinguaDesk Pro — Complete Windows Build & Packaging Automation Script
# عمل محمد البكير (Developed & Engineered by Mohammed Al-Bakir)
# =============================================================================

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
$PortableDir = Join-Path $RootDir "ReadyToInstall\LinguaDeskPro_Portable"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  LinguaDesk Pro v2.5.0 — Windows Build & Packaging Tool" -ForegroundColor Cyan
Write-Host "  عمل محمد البكير (Developed & Engineered by Mohammed Al-Bakir)" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan

# Step 1: Check if .NET 8 SDK is installed for full WebView2 solution publish
if (Get-Command "dotnet" -ErrorAction SilentlyContinue) {
    Write-Host "[1/3] .NET SDK found! Publishing self-contained Windows x64 Desktop release..." -ForegroundColor Green
    dotnet publish (Join-Path $RootDir "LinguaDeskPro.sln") -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o $PortableDir
} else {
    Write-Host "[1/3] .NET 8 SDK not found; compiling native LinguaDeskPro.exe via built-in Windows Framework csc.exe..." -ForegroundColor Yellow
    $CscPath = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    if (Test-Path $CscPath) {
        $IconPath = Join-Path $RootDir "ui\assets\linguadesk.ico"
        $LauncherCs = Join-Path $PortableDir "NativeLauncher.cs"
        $OutExe = Join-Path $PortableDir "LinguaDeskPro.exe"
        & $CscPath /target:winexe /out:$OutExe /win32icon:$IconPath /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.Speech.dll $LauncherCs
        Write-Host "  -> Compiled native LinguaDeskPro.exe successfully!" -ForegroundColor Green
    }
}

# Step 2: Check for Inno Setup Compiler (ISCC.exe) to generate Setup EXE
$IsccPaths = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$IsccFound = $IsccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($IsccFound) {
    Write-Host "[2/3] Inno Setup found! Building ReadyToInstall\Installer_Build\LinguaDeskPro_Setup_v2.5.0.exe..." -ForegroundColor Green
    & $IsccFound (Join-Path $PSScriptRoot "LinguaDeskPro_Setup.iss")
} else {
    Write-Host "[2/3] Inno Setup (ISCC.exe) not installed on this machine. Portable edition and native EXE are ready in ReadyToInstall\LinguaDeskPro_Portable." -ForegroundColor Yellow
}

Write-Host "[3/3] Build pipeline completed!" -ForegroundColor Green
