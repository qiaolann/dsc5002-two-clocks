$ErrorActionPreference = "Stop"
$root = "D:\上课2026下\DSC5002 exploraty data analysis and visualization\project"
$dir = Join-Path $root "report\latex_deps"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$env:HTTP_PROXY  = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"

$files = @(
    @{ url = "https://mirrors.ctan.org/macros/latex/contrib/llncs/llncs.cls"; name = "llncs.cls" },
    @{ url = "https://mirrors.ctan.org/macros/latex/contrib/llncs/splncs04.bst"; name = "splncs04.bst" }
)

foreach ($f in $files) {
    $out = Join-Path $dir $f.name
    Write-Output ("fetching " + $f.name + " ...")
    Invoke-WebRequest -Uri $f.url -OutFile $out -UseBasicParsing -TimeoutSec 90
    $size = (Get-Item $out).Length
    Write-Output ("  saved " + $f.name + " (" + $size + " bytes)")
}

Get-ChildItem $dir | ForEach-Object { Write-Output ("  have: " + $_.Name + " " + $_.Length) }
