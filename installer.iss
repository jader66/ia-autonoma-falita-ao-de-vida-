#define MyAppName "Assistente"
#define MyAppVersion "1.3.0"
#define MyAppPublisher "Assistente"
#define MyAppExeName "Assistente.exe"

[Setup]
AppId={{7E1B7A75-8A89-4E0B-9D8D-ASSISTENTE13}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Assistente
DefaultGroupName=Assistente
OutputDir=installer
OutputBaseFilename=Assistente-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=
DisableProgramGroupPage=yes

[Files]
Source: "dist\Assistente.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Assistente"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Assistente"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar Assistente"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\models"
