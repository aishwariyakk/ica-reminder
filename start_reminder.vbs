' start_reminder.vbs
' Launches the ICA Reminder in the background with NO visible terminal window.
' Task Scheduler runs this file at login instead of python.exe directly.

Dim objShell
Set objShell = CreateObject("WScript.Shell")

' Change the path below if your project lives somewhere else.
objShell.Run "python -m ica_reminder.reminder", 0, False

Set objShell = Nothing
