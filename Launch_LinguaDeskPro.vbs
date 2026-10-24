' ============================================================================
' LinguaDesk Pro v7.0 Ultimate — Unified Single-App & Single-Shortcut Launcher
' عمل المهندس: محمد البكير (Mohammed Albukeer — mohammedalbukeer@gmail.com)
' ============================================================================
Option Explicit
On Error Resume Next

Dim fso, shell, scriptDir, exePath, singleExePath, csFile, csc64, csc32, cscExe, buildCmd
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = scriptDir

singleExePath = scriptDir & "\LinguaDeskPro_SingleFile.exe"
exePath = scriptDir & "\LinguaDeskPro.exe"
csFile = scriptDir & "\src\LinguaDeskPro.SingleExe\Program.cs"
If Not fso.FileExists(csFile) Then
    csFile = scriptDir & "\src\LinguaDeskPro.Desktop\LinguaDeskPro_DesktopHost.cs"
End If

' 1. Compile LinguaDeskPro.exe if not already compiled
If Not fso.FileExists(exePath) And fso.FileExists(csFile) Then
    csc64 = shell.ExpandEnvironmentStrings("%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe")
    csc32 = shell.ExpandEnvironmentStrings("%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe")
    cscExe = ""
    If fso.FileExists(csc64) Then
        cscExe = csc64
    ElseIf fso.FileExists(csc32) Then
        cscExe = csc32
    End If

    If cscExe <> "" Then
        buildCmd = """" & cscExe & """ /nologo /target:winexe /optimize+ /out:""" & exePath & """ /r:System.dll /r:System.Drawing.dll /r:System.Windows.Forms.dll /r:System.IO.Compression.dll /r:System.IO.Compression.FileSystem.dll """ & csFile & """"
        shell.Run buildCmd, 0, True
    End If
End If

' 2. Create ONLY ONE Desktop Shortcut ("LinguaDesk Pro.lnk") and delete any old second shortcut
Dim deskFolders(2), i, d, sc1, oldSecondLnk, iconFile
deskFolders(0) = shell.SpecialFolders("Desktop")
deskFolders(1) = shell.ExpandEnvironmentStrings("%USERPROFILE%\Desktop")
deskFolders(2) = shell.ExpandEnvironmentStrings("%USERPROFILE%\OneDrive\Desktop")
iconFile = scriptDir & "\ui\assets\linguadesk.ico"
If Not fso.FileExists(iconFile) Then iconFile = "shell32.dll,13"

For i = 0 To 2
    d = deskFolders(i)
    If d <> "" And fso.FolderExists(d) Then
        oldSecondLnk = d & "\LinguaDesk Floating Translator.lnk"
        If fso.FileExists(oldSecondLnk) Then
            fso.DeleteFile oldSecondLnk, True
        End If

        Set sc1 = shell.CreateShortcut(d & "\LinguaDesk Pro.lnk")
        If fso.FileExists(singleExePath) Then
            sc1.TargetPath = singleExePath
        ElseIf fso.FileExists(exePath) Then
            sc1.TargetPath = exePath
        Else
            sc1.TargetPath = shell.ExpandEnvironmentStrings("%WINDIR%\System32\wscript.exe")
            sc1.Arguments = """" & WScript.ScriptFullName & """"
        End If
        sc1.WorkingDirectory = scriptDir
        sc1.Description = "LinguaDesk Pro v7.0 — عمل محمد البكير (Mohammed Albukeer)"
        sc1.IconLocation = iconFile
        sc1.Save
    End If
Next

' 3. Launch ONLY ONE Application instance (LinguaDeskPro.exe opens the Main Window + Background Hotkey Engine)
If fso.FileExists(singleExePath) Then
    shell.Run """" & singleExePath & """", 1, False
    WScript.Quit 0
ElseIf fso.FileExists(exePath) Then
    shell.Run """" & exePath & """", 1, False
    WScript.Quit 0
End If
