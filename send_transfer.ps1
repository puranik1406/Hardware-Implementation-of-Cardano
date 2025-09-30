$ErrorActionPreference = 'Stop'

# Paths
$KeyPath = "C:\Users\dhwin\ActuAlte M1\arduino-brisumi-satoshi-real-system\keys\preprod.payment.cborHex.txt"
$OutPath = Join-Path $env:TEMP 'masumi_transfer.json'
$Url = 'http://localhost:3001/api/cardano/transfer'

if (-not (Test-Path -LiteralPath $KeyPath)) {
  throw "Signing key file not found: $KeyPath"
}

# Read and trim CBOR hex
$cbor = (Get-Content -LiteralPath $KeyPath -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($cbor)) {
  throw "Signing key CBOR file is empty: $KeyPath"
}

# Build JSON body
$body = [pscustomobject]@{
  fromAgent = 'satoshi_alpha_001'
  toAgent   = 'satoshi_beta_002'
  amountAda = 1
  skeyCbor  = $cbor
}

# Write request to a file to avoid quoting issues
$body | ConvertTo-Json -Compress | Set-Content -LiteralPath $OutPath -Encoding UTF8
Write-Host "Prepared request body at: $OutPath"

# Send request
try {
  $resp = Invoke-RestMethod -Uri $Url -Method Post -ContentType 'application/json' -InFile $OutPath -TimeoutSec 120
  Write-Host "Response:" -ForegroundColor Cyan
  $resp | ConvertTo-Json -Depth 6
} catch {
  Write-Host "Request failed:" -ForegroundColor Red
  $_.Exception.Message
  if ($_.ErrorDetails) { $_.ErrorDetails.Message }
  throw
}
