param(
  [Parameter(Mandatory=$true)][string]$SkeyPath
)

# Extract cborHex value from a cardano-cli .skey JSON so we can set AGENT1_SKEY_CBOR easily.

$ErrorActionPreference = 'Stop'
if (!(Test-Path $SkeyPath)) { Write-Error "File not found: $SkeyPath" }

try {
  $json = Get-Content -Raw -Path $SkeyPath | ConvertFrom-Json
} catch {
  Write-Error "Failed to parse JSON: $_"
}

if ($null -eq $json.cborHex) { Write-Error "No cborHex field found in $SkeyPath" }

Write-Host $json.cborHex
