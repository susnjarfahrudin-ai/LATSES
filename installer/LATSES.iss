#define AppName "LAT-CES Scientific Engineering"
#define AppVersion "1.2.0"
#define AppPublisher "LATSES"
#define AppExeName "LATSES.exe"

[Setup]
AppId={{B7C2C2F6-4B0B-4F65-9A19-6A0FAD8D5A11}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\LAT-CES
DefaultGroupName=LAT-CES
OutputDir=installer-output
OutputBaseFilename=LAT-CES-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
Uninstallable=yes

[Files]
Source: "..\dist\LATSES.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LAT-CES Scientific Engineering"; Filename: "{app}\LATSES.exe"
Name: "{userdesktop}\LAT-CES Scientific Engineering"; Filename: "{app}\LATSES.exe"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Run]
Filename: "{app}\LATSES.exe"; Description: "Start LAT-CES Scientific Engineering"; Flags: nowait postinstall skipifsilent
