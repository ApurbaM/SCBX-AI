# Build dist/SCBX-local-demo.zip for sharing (Windows PowerShell)
# Run from repo root:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\make_share_zip.ps1

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

$dist = Join-Path $root "dist"
if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist | Out-Null }

$zipPath = Join-Path $dist "SCBX-local-demo.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

$excludeDirs = @(
  ".git", "node_modules", "__pycache__", ".cursor", "dist", "terminals"
) | ForEach-Object { $_.ToLowerInvariant() }

$excludeFiles = @("SCBX-local-demo.zip")

$items = Get-ChildItem -LiteralPath $root -Force | Where-Object {
  $n = $_.Name.ToLowerInvariant()
  if ($_.PSIsContainer) {
    return $excludeDirs -notcontains $n
  }
  return $excludeFiles -notcontains $_.Name
}

Write-Host "Zipping from: $root"
Write-Host "Output: $zipPath"
Compress-Archive -Path ($items.FullName) -DestinationPath $zipPath -CompressionLevel Optimal -Force
Write-Host "Done. Share: $zipPath"
