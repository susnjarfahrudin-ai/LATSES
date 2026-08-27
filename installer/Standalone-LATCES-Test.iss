#define AppName "LAT-CES Standalone Test"
#define AppVersion "0.1.0-test"
#define AppPublisher "LATCES Standalone Test"
#define AppExeName "LAT-CES-Standalone-Test.exe"

[Setup]
AppId={{C6D2D7AF-6F56-4F87-8F80-4C2C7F1D52C1}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\LAT-CES Standalone Test
DefaultGroupName=LAT-CES Standalone Test
OutputDir=..\installer-output-standalone
OutputBaseFilename=LAT-CES-Standalone-Test-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
Uninstallable=yes

[Files]
Source: "..\dist\LAT-CES-Standalone-Test.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LAT-CES Standalone Test"; Filename: "{app}\{#AppExeName}"
Name: "{userdesktop}\LAT-CES Standalone Test"; Filename: "{app}\{#AppExeName}"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Start LAT-CES Standalone Test"; Flags: nowait postinstall skipifsilent
