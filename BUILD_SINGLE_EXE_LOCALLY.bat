@echo off
chcp 65001 >nul
title بناء الملف التنفيذي الموحد LinguaDeskPro_SingleFile.exe — عمل محمد البكير (Mohammed Albukeer)
echo ============================================================================
echo   بناء ملف تنفيذي واحد شامل (LinguaDeskPro_SingleFile.exe)
echo   تصميم وتطوير المهندس: محمد البكير (Mohammed Albukeer)
echo   للتواصل: mohammedalbukeer@gmail.com
echo ============================================================================
echo.
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo [1/3] جاري ضغط القاموس (145,935 مدخلاً) ومحرك OCR والواجهة داخل EmbeddedPayload.zip ...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop'; " ^
  "$root = '%ROOT%'; " ^
  "$stage = Join-Path $env:TEMP 'LinguaDeskPro_SingleBuild'; " ^
  "if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }; " ^
  "New-Item -ItemType Directory -Force -Path $stage | Out-Null; " ^
  "Copy-Item (Join-Path $root 'ui') (Join-Path $stage 'ui') -Recurse -Force; " ^
  "Copy-Item (Join-Path $root 'resources') (Join-Path $stage 'resources') -Recurse -Force; " ^
  "Copy-Item (Join-Path $root 'scripts') (Join-Path $stage 'scripts') -Recurse -Force; " ^
  "$zip = Join-Path $root 'src\LinguaDeskPro.SingleExe\EmbeddedPayload.zip'; " ^
  "if (Test-Path $zip) { Remove-Item $zip -Force }; " ^
  "Add-Type -AssemblyName System.IO.Compression.FileSystem; " ^
  "[System.IO.Compression.ZipFile]::CreateFromDirectory($stage, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false); " ^
  "Write-Host '  [OK] EmbeddedPayload.zip Ready!'"

echo [2/3] جاري ترجمة ودمج كل شيء في ملف تنفيذي واحد مستقل (LinguaDeskPro_SingleFile.exe) ...
set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" set "CSC=%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe"

"%CSC%" /nologo /target:winexe /optimize+ ^
  /out:"%ROOT%\LinguaDeskPro_SingleFile.exe" ^
  /r:System.dll /r:System.Drawing.dll /r:System.Windows.Forms.dll /r:System.IO.Compression.dll /r:System.IO.Compression.FileSystem.dll ^
  /resource:"%ROOT%\src\LinguaDeskPro.SingleExe\EmbeddedPayload.zip",LinguaDeskProHost.EmbeddedPayload.zip ^
  "%ROOT%\src\LinguaDeskPro.SingleExe\Program.cs"

if exist "%ROOT%\LinguaDeskPro_SingleFile.exe" (
    echo.
    echo [3/3] تم بنجاح إنشاء الملف التنفيذي الموحد:
    echo       %ROOT%\LinguaDeskPro_SingleFile.exe
    echo       يمكنك نسخ هذا الملف الوحيد إلى أي مكان أو تثبيته وتشغيله مباشرة!
    start "" "%ROOT%\LinguaDeskPro_SingleFile.exe" --install-and-run
) else (
    echo [!] تعذر بناء الملف الموحد.
    pause
)
