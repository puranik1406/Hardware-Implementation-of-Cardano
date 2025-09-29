param(
  [string]$OutDir = "keys",
  [string]$Network = "preprod",
  [switch]$Force
)

# This script requires `cardano-cli` in PATH. Install from IOHK or your package manager.
# It creates a payment signing key, verification key, and a bech32 address for Cardano preprod.

$ErrorActionPreference = 'Stop'

if (!(Get-Command cardano-cli -ErrorAction SilentlyContinue)) {
  Write-Error "cardano-cli not found in PATH. Install it before running this script."
}

# Resolve network flag
$netFlag = if ($Network -eq 'preprod') { '--testnet-magic 1' } elseif ($Network -eq 'preview') { '--testnet-magic 2' } else { '--mainnet' }
Write-Host "Using network: $Network ($netFlag)"

# Prepare output directory
$fullOut = Join-Path -Path (Get-Location) -ChildPath $OutDir
if (!(Test-Path $fullOut)) { New-Item -ItemType Directory -Force -Path $fullOut | Out-Null }

$prefix = if ($Network -eq 'preprod') { 'preprod' } else { $Network }
$skey = Join-Path $fullOut "$prefix.payment.skey"
$vkey = Join-Path $fullOut "$prefix.payment.vkey"
$addr = Join-Path $fullOut "$prefix.payment.addr"

if ((Test-Path $skey) -and -not $Force) { Write-Error "Signing key exists: $skey (use -Force to overwrite)" }

# Generate keys
cardano-cli address key-gen `
  --verification-key-file $vkey `
  --signing-key-file $skey

# Build address
cardano-cli address build `
  --payment-verification-key-file $vkey `
  --out-file $addr `
  $netFlag

Write-Host "Generated files:"
Write-Host "  $skey"
Write-Host "  $vkey"
Write-Host "  $addr"

Write-Host "Address:"
Get-Content $addr
