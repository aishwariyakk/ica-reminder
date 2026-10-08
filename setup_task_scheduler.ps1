# setup_task_scheduler.ps1
# Installs ICA Reminder to the Windows Startup folder so it launches
# automatically on every login — no Admin rights required.
#
# How to run:
#   1. Open a normal PowerShell terminal (no Admin needed)
#   2. cd to this project folder
#   3. Run:  .\setup_task_scheduler.ps1

$ProjectDir  = $PSScriptRoot
$VbsPath     = Join-Path $ProjectDir "start_reminder.vbs"
$StartupDir  = [Environment]::GetFolderPath("Startup")
$ShortcutDst = Join-Path $StartupDir "ICA Reminder.lnk"

# ── Check that start_reminder.vbs exists ─────────────────────────────────────
if (-not (Test-Path $VbsPath)) {
    Write-Error "start_reminder.vbs not found in $ProjectDir. Aborting."
    exit 1
}

# ── Create a shortcut in the Startup folder ───────────────────────────────────
$WshShell  = New-Object -ComObject WScript.Shell
$Shortcut  = $WshShell.CreateShortcut($ShortcutDst)
$Shortcut.TargetPath       = "wscript.exe"
$Shortcut.Arguments        = "`"$VbsPath`""
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description      = "ICA Reminder - daily IBM Consulting Advantage nudge"
$Shortcut.Save()

Write-Host ""
Write-Host "OK  Startup shortcut created successfully." -ForegroundColor Green
Write-Host ("    Location : " + $ShortcutDst)
Write-Host "    ICA Reminder will now launch automatically every time you log in."
Write-Host ""
Write-Host "To remove auto-start, delete the shortcut:"
Write-Host ("  Remove-Item '" + $ShortcutDst + "'")
Write-Host ""
Write-Host "To start it right now without logging out:"
$StartCmd = 'Start-Process wscript.exe -ArgumentList \"' + $VbsPath + '\"'
Write-Host ("  " + $StartCmd)
