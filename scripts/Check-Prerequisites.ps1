# =============================================================================
# LinguaDesk Pro — System Prerequisite & Integrity Checker for Windows
# عمل محمد البكير (Developed & Engineered by Mohammed Al-Bakir)
# =============================================================================

Write-Host "=== فحص متطلبات تشغيل LinguaDesk Pro على Windows (عمل محمد البكير) ===" -ForegroundColor Cyan
Write-Host "1. نظام التشغيل: $([System.Environment]::OSVersion.VersionString)" -ForegroundColor Green

$Csc = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (Test-Path $Csc) {
    Write-Host "2. مترجم .NET المدمج في ويندوز (csc.exe): متوفر وجاهز" -ForegroundColor Green
}

if (Get-Command "dotnet" -ErrorAction SilentlyContinue) {
    Write-Host "3. حزمة تطوير .NET SDK: متوفرة ($(dotnet --version))" -ForegroundColor Green
} else {
    Write-Host "3. حزمة .NET 8 SDK: غير مثبتة (اختيارية لبناء مشروع WebView2 من المصدر)" -ForegroundColor Yellow
}

Add-Type -AssemblyName System.Speech
$Synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$Voices = $Synth.GetInstalledVoices()
Write-Host "4. أصوات النطق المحلية المثبتة في ويندوز (SAPI5): $($Voices.Count) صوت" -ForegroundColor Green
foreach ($v in $Voices) {
    Write-Host "   - $($v.VoiceInfo.Name) ($($v.VoiceInfo.Culture))"
}
