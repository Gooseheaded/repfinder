Write-Output "Installing Python 3.10."
winget install -e --id Python.Python.3.10

Write-Output "Installing the latest version of Repfinder!"
& .\update_windows.ps1

Write-Output "Repfinder should have been installed...! Open a NEW terminal, and run \"run_windows.ps1\" to use Repfinder!"