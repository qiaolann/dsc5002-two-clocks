# Install a LaTeX engine (Tectonic), the VS Code LaTeX extension, and configure
# the workspace so Ctrl+S compiles and Ctrl+Alt+V previews.
$ErrorActionPreference = "Stop"
$root = "D:\上课2026下\DSC5002 exploraty data analysis and visualization\project"
$bin = Join-Path $env:USERPROFILE "bin"
New-Item -ItemType Directory -Force -Path $bin | Out-Null

function Write-Step($t) { Write-Host "`n== $t ==" -ForegroundColor Cyan }

# ---------------------------------------------------------------- 1. tectonic
Write-Step "Tectonic (LaTeX engine)"
$exe = Join-Path $bin "tectonic.exe"
if (Test-Path $exe) {
    Write-Host "already installed: $exe"
} else {
    $api = Invoke-RestMethod -Uri "https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest" `
        -Headers @{ "User-Agent" = "dsh" } -TimeoutSec 60
    $asset = $api.assets | Where-Object { $_.name -match "windows.*msvc.*\.zip$" } | Select-Object -First 1
    if (-not $asset) { throw "no windows asset in the latest release" }
    Write-Host ("downloading " + $asset.name + " (" + [math]::Round($asset.size/1MB,1) + " MB)")
    $zip = Join-Path $env:TEMP $asset.name
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zip -UseBasicParsing -TimeoutSec 600
    $tmp = Join-Path $env:TEMP "tectonic_extract"
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    $found = Get-ChildItem $tmp -Filter tectonic.exe -Recurse | Select-Object -First 1
    if (-not $found) { throw "tectonic.exe not found in the archive" }
    Copy-Item $found.FullName $exe -Force
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Write-Host "installed: $exe"
}

# ---------------------------------------------------------------- 2. PATH
Write-Step "Adding $bin to the user PATH"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$bin*") {
    [Environment]::SetEnvironmentVariable("Path", "$bin;$userPath", "User")
    Write-Host "PATH updated (restart VS Code / terminals to pick it up)"
} else {
    Write-Host "already on PATH"
}
$env:Path = "$bin;$env:Path"

# ---------------------------------------------------------------- 3. extension
Write-Step "VS Code extension: LaTeX Workshop"
$code = "E:\vscode\Microsoft VS Code\bin\code.cmd"
if (Test-Path $code) {
    & $code --install-extension James-Yu.latex-workshop --force
} else {
    Write-Host "VS Code CLI not found at $code - install the extension manually"
}

# ---------------------------------------------------------------- 4. test build
Write-Step "Test build of report.tex (first run downloads packages, be patient)"
Push-Location (Join-Path $root "report")
try {
    & $exe -X compile report.tex
    if (Test-Path "report.pdf") {
        Write-Host "`nOK: report.pdf built" -ForegroundColor Green
        Write-Host ("size: " + [math]::Round((Get-Item report.pdf).Length/1KB) + " KB")
    } else {
        Write-Host "build finished but no PDF - see the messages above" -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}

Write-Host "`nDone. Restart VS Code, open the 'project' folder, open report/report.tex, press Ctrl+Alt+V." -ForegroundColor Green
