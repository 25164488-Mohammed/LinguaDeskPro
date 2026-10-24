; =============================================================================
; LinguaDesk Pro — Inno Setup Professional Windows Installer Script
; عمل محمد البكير (Developed & Engineered by Mohammed Al-Bakir)
; =============================================================================

#define MyAppName "LinguaDesk Pro"
#define MyAppVersion "2.5.0"
#define MyAppPublisher "عمل محمد البكير (Mohammed Al-Bakir)"
#define MyAppExeName "LinguaDeskPro.exe"

[Setup]
AppId={{8F9E3A21-5B4C-4D7A-9E12-C0FFEE2026AB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
SetupIconFile=..\ui\assets\linguadesk.ico
UninstallDisplayIcon={app}\ui\assets\linguadesk.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\ReadyToInstall\Installer_Build
OutputBaseFilename=LinguaDeskPro_Setup_v2.5.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "تشغيل LinguaDesk Pro تلقائياً عند بدء تشغيل Windows (اختياري)"; GroupDescription: "خيارات بدء التشغيل:"; Flags: unchecked

[Files]
Source: "..\ReadyToInstall\LinguaDeskPro_Portable\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\ui\assets\linguadesk.ico"
Name: "{group}\إلغاء تثبيت {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\ui\assets\linguadesk.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startup

[UninstallDelete]
; Remove temporary runtime cache files without deleting user's saved vocabulary backups
Type: filesandordirs; Name: "{localappdata}\Temp\linguadesk_*"

[Code]
function InitializeSetup(): Boolean;
var
  Wv2Key: String;
begin
  Result := True;
  Wv2Key := 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  if not RegKeyExists(HKLM, Wv2Key) and not RegKeyExists(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}') then
  begin
    MsgBox('تنبيه: لم يتم رصد Microsoft Edge WebView2 Runtime في السجل القياسي. سيعمل التطبيق عبر مشغل سطح المكتب المدمج أو يمكنك تثبيت WebView2 Runtime عند الحاجة.', mbInformation, MB_OK);
  end;
end;
