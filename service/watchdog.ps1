# Shoh gateway watchdog. Run by Task Scheduler at logon and every 5 minutes, hidden (conhost --headless).
# ASCII only: Windows PowerShell 5.1 reads BOM-less UTF-8 as ANSI.
#
# Why `hermes gateway start` and not `gateway run` / raw python:
#   A process started inside a scheduled task (or a terminal, or an agent shell) lives in that parent's
#   Job Object and console. When the parent ends or hits its time limit, Windows kills it with no exit
#   record - the Telegram bot silently goes offline. `hermes gateway start` uses Hermes' own detached
#   spawn (CREATE_BREAKAWAY_FROM_JOB + CREATE_NO_WINDOW + new process group): the gateway leaves the
#   parent's job, gets its own hidden console, survives the task, and no window ever appears.
#   It is idempotent: if the gateway is already running it only reports that.
param(
    [Parameter(Mandatory = $true)][string]$HermesHome,
    [string]$ProfileName = "ieltschannel"
)
$ErrorActionPreference = "Continue"
$exe = Join-Path $HermesHome "bin\hermes.exe"
$logDir = Join-Path $HermesHome "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir "shoh-watchdog.log"

$env:HERMES_HOME = $HermesHome
$env:HERMES_GATEWAY_INSTALL_START_ON_LOGIN = "0"   # never prompt from a hidden task

$out = & $exe -p $ProfileName gateway start 2>&1 | Out-String
$one = ($out -replace '\s+', ' ').Trim()
if ($one.Length -gt 300) { $one = $one.Substring(0, 300) }
# Log only real starts and errors, not the every-5-minutes "already running".
if ($one -notmatch 'already running') {
    Add-Content -LiteralPath $log -Value ("{0} [{1}] {2}" -f (Get-Date -Format s), $ProfileName, $one)
}

# Keep the log small.
if ((Test-Path -LiteralPath $log) -and (Get-Item -LiteralPath $log).Length -gt 512KB) {
    $tail = @(Get-Content -LiteralPath $log -Tail 500)   # read fully before rewriting the same file
    Set-Content -LiteralPath $log -Value $tail
}
