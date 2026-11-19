# Installs the Shoh gateway autostart: one per-user scheduled task that runs service\watchdog.ps1
#   - at logon (30 s delay)  -> bot comes back by itself after the laptop is turned off and on
#   - every 5 minutes        -> bot comes back by itself if the gateway ever dies
#   - hidden                 -> conhost --headless, no terminal window; gateway itself is windowless
# No admin rights needed. ASCII only.
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\service\install-autostart.ps1 -HermesHome "D:\Hermes" [-ProfileName ieltschannel]
#   ... -Uninstall      removes the task
param(
    [Parameter(Mandatory = $true)][string]$HermesHome,
    [string]$ProfileName = "ieltschannel",
    [string]$TaskName = "",
    [switch]$Uninstall,
    [switch]$NoStartNow
)
$ErrorActionPreference = "Stop"
if (-not $TaskName) { $TaskName = "Shoh_Gateway_Watchdog_$ProfileName" }

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task $TaskName"
    return
}

$HermesHome = [System.IO.Path]::GetFullPath($HermesHome)
if (-not (Test-Path -LiteralPath (Join-Path $HermesHome "bin\hermes.exe"))) { throw "hermes.exe not found in $HermesHome\bin" }

# Copy the watchdog next to Hermes so it keeps working even if the package folder is moved or deleted.
$svcDir = Join-Path $HermesHome "shoh-service"
New-Item -ItemType Directory -Force -Path $svcDir | Out-Null
$wd = Join-Path $svcDir "watchdog.ps1"
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "watchdog.ps1") -Destination $wd -Force

$psArgs = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$wd`" -HermesHome `"$HermesHome`" -ProfileName $ProfileName"
# conhost --headless (Windows 10 1809+/11) runs PowerShell without creating any visible console window.
$action = New-ScheduledTaskAction -Execute "conhost.exe" -Argument "--headless powershell.exe $psArgs" -WorkingDirectory $HermesHome

$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$logon = New-ScheduledTaskTrigger -AtLogOn -User $user
$logon.Delay = "PT30S"
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -Hidden
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($logon, $repeat) -Settings $settings `
    -Principal $principal -Description "Keeps the Shoh (Hermes $ProfileName) Telegram gateway running, hidden." -Force | Out-Null
Write-Host "Installed scheduled task $TaskName (logon + every 5 min, hidden)."

if (-not $NoStartNow) {
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Started. Log: $HermesHome\logs\shoh-watchdog.log"
}
