; JARVIS WorkMode v3 Installer
; Build: makensis jarvis_installer.nsi

!define APP_NAME    "JARVIS WorkMode"
!define APP_VERSION "3.0.0"
!define APP_EXE     "JarvisWorkMode.exe"
!define INSTALL_DIR "$PROGRAMFILES64\JarvisWorkMode"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "JarvisWorkMode_Setup_v${APP_VERSION}.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

!include "MUI2.nsh"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch JARVIS WorkMode"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Main"
  SetOutPath "$INSTDIR"
  File "..\dist\${APP_EXE}"
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "DisplayName" "${APP_NAME}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "DisplayVersion" "${APP_VERSION}"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}.lnk"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "JarvisWorkMode"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode"
SectionEnd
