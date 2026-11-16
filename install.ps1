# Shoh (IELTSSHOKH) agent installer for Hermes Agent v0.23.1 on Windows.
# ASCII only: Windows PowerShell 5.1 reads BOM-less UTF-8 as ANSI.
# Usage (from the unpacked package folder):
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -HermesHome "D:\Hermes" [-ProfileName ieltschannel] [-KnowledgeDir "D:\Shoh\knowledge"] [-HermesSource "D:\Hermes\hermes-agent"]
param(
    [Parameter(Mandatory = $true)][string]$HermesHome,
    [string]$ProfileName = "ieltschannel",
    [string]$KnowledgeDir = "",
    [string]$HermesSource = "",
    [ValidateSet("codex", "claude", "gemini", "openrouter")][string]$Model = "codex",
    [string]$AdminTelegramId = "",
    [string]$TeacherTelegramId = "",
    [switch]$SkipPatches,
    [switch]$NoAlias
)
# Native tools (hermes, git) write progress to stderr; PS 5.1 would turn that into a
# terminating error under "Stop". Check $LASTEXITCODE for them and use -ErrorAction Stop on file ops.
$ErrorActionPreference = "Continue"
$pkg = Split-Path -Parent $MyInvocation.MyCommand.Path
function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

if ($ProfileName -notmatch '^[a-z0-9-]+$') { throw "Profile name must be lowercase letters, digits or '-'." }
$exe = Join-Path $HermesHome "bin\hermes.exe"
if (-not (Test-Path -LiteralPath $exe)) {
    $cmd = Get-Command hermes -ErrorAction SilentlyContinue
    if (-not $cmd) { throw "Hermes not found at $exe and not on PATH. Install Hermes Agent v0.23.1 first." }
    $exe = $cmd.Source
}
$env:HERMES_HOME = $HermesHome

Step "Hermes version"
$verOut = @(& $exe --version 2>&1)
if ($LASTEXITCODE -ne 0) { throw "hermes --version failed: $($verOut -join ' ')" }
$ver = [string]$verOut[0]
Write-Host $ver
if ("$ver" -notmatch "v0\.23\.") { Write-Warning "Package was tested on Hermes v0.23.1. Patches may not apply on $ver." }

# 1. Profile
$profDir = Join-Path $HermesHome "profiles\$ProfileName"
if (-not (Test-Path -LiteralPath $profDir)) {
    Step "Creating profile $ProfileName"
    $createArgs = @("profile", "create", $ProfileName, "--no-skills", "--description", "IELTS Telegram channel analysis, drafts and owner-reviewed publishing.")
    if ($NoAlias) { $createArgs += "--no-alias" }
    & $exe @createArgs
    if ($LASTEXITCODE -ne 0) { throw "hermes profile create failed" }
    if (-not (Test-Path -LiteralPath $profDir)) { throw "Hermes created the profile outside $HermesHome. Re-run with -HermesHome set to the Hermes home that contains the profiles folder." }
} else {
    Step "Profile exists; backing up SOUL, memories, plugins, skills, config"
    $bak = Join-Path $profDir ("backups\pre-install-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
    New-Item -ItemType Directory -Force -Path $bak -ErrorAction Stop | Out-Null
    foreach ($item in "SOUL.md", "config.yaml", "memories", "plugins", "skills") {
        $src = Join-Path $profDir $item
        if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination $bak -Recurse -Force -ErrorAction Stop }
    }
    Write-Host "Backup: $bak"
}

# 2. Knowledge directory (client-owned, outside Hermes)
if (-not $KnowledgeDir) { $KnowledgeDir = Join-Path $HermesHome "shoh-knowledge" }
$KnowledgeDir = [System.IO.Path]::GetFullPath($KnowledgeDir)
Step "Knowledge -> $KnowledgeDir"
New-Item -ItemType Directory -Force -Path $KnowledgeDir -ErrorAction Stop | Out-Null
Get-ChildItem -LiteralPath (Join-Path $pkg "knowledge") -File | ForEach-Object {
    $dst = Join-Path $KnowledgeDir $_.Name
    if (Test-Path -LiteralPath $dst) { Write-Host "  keep existing $($_.Name)" } else { Copy-Item -LiteralPath $_.FullName -Destination $dst -ErrorAction Stop }
}

# 3. Persona, memory, plugin, skills
Step "Installing SOUL, memory, plugin and skills"
Copy-Item -LiteralPath (Join-Path $pkg "hermes\profile\SOUL.md") -Destination (Join-Path $profDir "SOUL.md") -Force -ErrorAction Stop
$mem = Join-Path $profDir "memories"
New-Item -ItemType Directory -Force -Path $mem -ErrorAction Stop | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $mem "MEMORY.md"))) {
    Copy-Item -LiteralPath (Join-Path $pkg "hermes\profile\MEMORY.md") -Destination (Join-Path $mem "MEMORY.md") -ErrorAction Stop
} else { Write-Host "  keep existing memories\MEMORY.md (learned preferences)" }
$plugDst = Join-Path $profDir "plugins\channel-knowledge"
New-Item -ItemType Directory -Force -Path $plugDst -ErrorAction Stop | Out-Null
Copy-Item -Path (Join-Path $pkg "hermes\plugins\channel-knowledge\*") -Destination $plugDst -Recurse -Force -ErrorAction Stop
$skillDst = Join-Path $profDir "skills"
New-Item -ItemType Directory -Force -Path $skillDst -ErrorAction Stop | Out-Null
Copy-Item -Path (Join-Path $pkg "hermes\skills\*") -Destination $skillDst -Recurse -Force -ErrorAction Stop

# 4. Config (model and Telegram secrets are NOT included; the client logs in with Hermes setup)
Step "Writing config.yaml"
$cfg = Get-Content -LiteralPath (Join-Path $pkg "config.template.yaml") -Raw
# Model presets: provider, default model, image provider, how the owner logs in.
# Change the model later with: hermes -p <profile> model
$models = @{
    codex      = @("openai-codex", "gpt-5.6-terra", "openai-codex", "hermes -p $ProfileName auth add openai-codex   (ChatGPT subscription)")
    claude     = @("anthropic", "claude-sonnet-5-5", "openai-codex", "put ANTHROPIC_API_KEY=... (or CLAUDE_CODE_OAUTH_TOKEN from 'claude setup-token') in profiles\$ProfileName\.env")
    gemini     = @("gemini", "gemini-3.7-flash", "openai-codex", "put GEMINI_API_KEY=... in profiles\$ProfileName\.env")
    openrouter = @("openrouter", "anthropic/claude-sonnet-5.5", "openrouter", "put OPENROUTER_API_KEY=... in profiles\$ProfileName\.env")
}
$m = $models[$Model]
$cfg = $cfg.Replace("__KNOWLEDGE_DIR__", ($KnowledgeDir -replace '\\', '/'))
$cfg = $cfg.Replace("__PROVIDER__", $m[0]).Replace("__MODEL__", $m[1]).Replace("__IMAGE_PROVIDER__", $m[2])
if ($AdminTelegramId) {
    $cfg = $cfg.Replace("__ADMIN_IDS__", "'" + $AdminTelegramId + "'")
} else {
    Write-Warning "No -AdminTelegramId: every allowed user can run every slash command."
    $cfg = ($cfg -split "`r?`n" | Where-Object { $_ -notmatch '__ADMIN_IDS__' }) -join "`n"
}
$null = [System.IO.File]::WriteAllText((Join-Path $profDir "config.yaml"), $cfg, (New-Object System.Text.UTF8Encoding($false)))

# 4b. Telegram allowed users (admin + teacher). The bot token is added by the owner via gateway setup.
$ids = @($AdminTelegramId, $TeacherTelegramId | Where-Object { $_ }) -join ","
if ($ids) {
    $envFile = Join-Path $profDir ".env"
    $lines = @()
    if (Test-Path -LiteralPath $envFile) { $lines = @(Get-Content -LiteralPath $envFile | Where-Object { $_ -notmatch '^TELEGRAM_ALLOWED_USERS=' }) }
    $lines += "TELEGRAM_ALLOWED_USERS=$ids"
    [System.IO.File]::WriteAllLines($envFile, [string[]]$lines)
}

# 4c. Free voice stack: local Whisper (speech-to-text, Uzbek + English auto-detect) and Edge TTS.
Step "Installing voice dependencies (edge-tts, faster-whisper)"
& $exe pm install --extra edge-tts --extra stt-whisper
if ($LASTEXITCODE -ne 0) { Write-Warning "Voice dependencies failed; Hermes installs them on first use." }

# 5. Hermes source patches (Telegram photo paths, Windows-safe document names)
if (-not $SkipPatches) {
    if (-not $HermesSource) { $HermesSource = Join-Path $HermesHome "hermes-agent" }
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git -and (Test-Path -LiteralPath (Join-Path $HermesSource ".git"))) {
        foreach ($p in Get-ChildItem -LiteralPath (Join-Path $pkg "hermes\patches") -Filter *.patch) {
            & git -C $HermesSource apply --check -R $p.FullName 2>$null
            if ($LASTEXITCODE -eq 0) { Write-Host "  already applied: $($p.Name)"; continue }
            & git -C $HermesSource apply --check $p.FullName
            if ($LASTEXITCODE -ne 0) { Write-Warning "  patch does not apply cleanly, skipped: $($p.Name)"; continue }
            & git -C $HermesSource apply $p.FullName
            Write-Host "  applied: $($p.Name)"
        }
    } else { Write-Warning "Hermes git checkout not found at $HermesSource; patches skipped. Use -HermesSource." }
}

# 6. Verify
Step "Verifying enabled tools"
& $exe -p $ProfileName tools --summary
Write-Host ""
Write-Host "Done. Next (owner steps):" -ForegroundColor Green
Write-Host "  1. Model login ($Model): $($m[3])"
Write-Host "     Fallback so Shoh never stops on a rate limit: hermes -p $ProfileName fallback add"
Write-Host "  2. Telegram bot:    hermes -p $ProfileName gateway setup   (bot token + allowed user id)"
Write-Host "  3. Smoke test:      hermes -p $ProfileName -z ""Kanal brend qoidalari qanday?"""
Write-Host "  4. Start gateway:   hermes -p $ProfileName gateway run"
Write-Host "  5. Google apps:     hermes -p $ProfileName connectors connect   (or ask Shoh in Telegram)"
Write-Host "  6. First chat: Shoh runs onboarding (teacher, channels, brand, Obsidian, Google, voice)."
Write-Host "  Updates: admin sends /update in Telegram, or run: hermes update"
