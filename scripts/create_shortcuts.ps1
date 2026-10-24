param(
    [string]$InstallDir = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "SilentlyContinue"
$wsh = New-Object -ComObject WScript.Shell

$desktopCandidates = @(
    [Environment]::GetFolderPath("Desktop"),
    (Join-Path $env:USERPROFILE "Desktop"),
    (Join-Path $env:USERPROFILE "OneDrive\Desktop"),
    (Join-Path $env:USERPROFILE "OneDrive - Personal\Desktop")
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

$exeFile = Join-Path $InstallDir "LinguaDeskPro.exe"
$icoFile = Join-Path $InstallDir "ui\assets\linguadesk.ico"

foreach ($desk in $desktopCandidates) {
    # Remove any old second shortcut so ONLY ONE shortcut exists
    $oldLnk = Join-Path $desk "LinguaDesk Floating Translator.lnk"
    if (Test-Path $oldLnk) { Remove-Item $oldLnk -Force -ErrorAction SilentlyContinue }

    $lnk1 = Join-Path $desk "LinguaDesk Pro.lnk"
    $sc1 = $wsh.CreateShortcut($lnk1)
    $sc1.TargetPath = $exeFile
    $sc1.WorkingDirectory = $InstallDir
    $sc1.Description = "LinguaDesk Pro v7.0 — عمل محمد البكير (Mohammed Albukeer)"
    if (Test-Path $icoFile) { $sc1.IconLocation = $icoFile }
    $sc1.Save()
}

$startMenu = [Environment]::GetFolderPath("Programs")
if ($startMenu -and (Test-Path $startMenu)) {
    $oldStart2 = Join-Path $startMenu "LinguaDesk Floating Translator.lnk"
    if (Test-Path $oldStart2) { Remove-Item $oldStart2 -Force -ErrorAction SilentlyContinue }

    $lnkStart = Join-Path $startMenu "LinguaDesk Pro.lnk"
    $scS = $wsh.CreateShortcut($lnkStart)
    $scS.TargetPath = $exeFile
    $scS.WorkingDirectory = $InstallDir
    $scS.Description = "LinguaDesk Pro v7.0 — عمل محمد البكير"
    if (Test-Path $icoFile) { $scS.IconLocation = $icoFile }
    $scS.Save()
}
