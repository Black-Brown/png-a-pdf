#define AppName "PNG a PDF"
#define AppVersion "1.2.0"

[Setup]
AppId={{8682EC3A-07F2-4D6F-A821-76098D48AF41}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
DefaultDirName={localappdata}\Programs\PNG a PDF
DefaultGroupName=PNG a PDF
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\INSTALACION.md
UninstallDisplayIcon={app}\PNG a PDF.exe
SetupIconFile=..\assets\app.ico
OutputDir=..\instalador
OutputBaseFilename=PNG-a-PDF-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes
VersionInfoVersion=1.2.0.0

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "..\app\PNG a PDF.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\INSTALACION.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\PNG a PDF\PNG a PDF"; Filename: "{app}\PNG a PDF.exe"
Name: "{userprograms}\PNG a PDF\Desinstalar PNG a PDF"; Filename: "{uninstallexe}"
Name: "{userdesktop}\PNG a PDF"; Filename: "{app}\PNG a PDF.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PNG a PDF.exe"; Description: "Abrir PNG a PDF"; Flags: nowait postinstall skipifsilent unchecked
