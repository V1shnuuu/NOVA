; JARVIS WorkMode Installer Script
; Build with: makensis jarvis_installer.nsi
; Prerequisites: NSIS installed from https://nsis.sourceforge.io

!define APP_NAME "JARVIS WorkMode"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "V1shnuuu"
!define APP_EXE "JarvisWorkMode.exe"
!define INSTALL_DIR "$PROGRAMFILES64\JarvisWorkMode"
!define UNINSTALLER "Uninstall.exe"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "JarvisWorkMode_Setup_v${APP_VERSION}.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKCU "Software\JarvisWorkMode" ""
RequestExecutionLevel admin
SetCompressor /SOLID lzma

; ── Modern UI ────────────────────────────────────────────────────────
!include "MUI2.nsh"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch JARVIS WorkMode now"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ── Install Section ──────────────────────────────────────────────────
Section "Main Application" SecMain
  SetOutPath "$INSTDIR"
  File "..\dist\${APP_EXE}"

  ; Start Menu & Desktop shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"

  ; Add/Remove Programs registry
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "DisplayName" "${APP_NAME}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "UninstallString" "$INSTDIR\${UNINSTALLER}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "Publisher" "${APP_PUBLISHER}"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode" \
              "EstimatedSize" 45000

  WriteUninstaller "$INSTDIR\${UNINSTALLER}"
SectionEnd

; ── Uninstall Section ────────────────────────────────────────────────
Section "Uninstall"
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\${UNINSTALLER}"
  RMDir "$INSTDIR"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\${APP_NAME}.lnk"

  ; Remove startup entry
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "JarvisWorkMode"

  ; Remove from Add/Remove Programs
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisWorkMode"
SectionEnd
