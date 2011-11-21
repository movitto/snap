; Snap windows installer
;--------------------------------
;Configuration
 
  ;General
  Name "Snap! System Snapshotter"
  OutFile "snap-installer.exe"
 
  ;Folder selection page
  InstallDir "$PROGRAMFILES\snap"
 
  ;Get install folder from registry if available
  InstallDirRegKey HKLM "SOFTWARE\Snap" ""

;---------------------------------
!Include "MUI.nsh"
 
!include "Sections.nsh"
!include "logiclib.nsh"
 
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Installer Section" inst_sec
  SetOutPath $INSTDIR
  File "dist\\library.zip"
  File "dist\\python27.dll"
  File "dist\\snaptool.exe"
  File "dist\\snap.conf"
  
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snap" \
                 "DisplayName" "Snap System Snapshotter"
                 
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snap" \
                 "Publisher" "Mo Morsi"                 
                 
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snap" \
                 "UninstallString" "$\"$INSTDIR\uninstaller.exe$\""
  
  ; TODO http://nsis.sourceforge.net/Signing_an_Uninstaller               
  writeUninstaller $INSTDIR\uninstaller.exe
SectionEnd

Section "un.Uninstaller Section" uinst_sec
  delete "$INSTDIR\\library.zip"
  delete "$INSTDIR\\python27.dll"
  delete "$INSTDIR\\snaptool.exe"
  delete "$INSTDIR\\uninstaller.exe"
  
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snap"
SectionEnd