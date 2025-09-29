$ErrorActionPreference = 'Stop'

# Config
$FromAddr = 'addr_test1vq588y6u6evwpgwhp4mnca55pfd4ez2epye5unw8dqhqsksr5kj4w'
$ToAddr   = 'addr_test1qqxdsjedg0fpurjt345lymmyxrs2r4u7etwchfwze7fwvfx76eyhp6agt96xprlux3tgph0zm5degavwkge2f9jmszqqg3p703'
$AmountLovelace = 1000000
$KeyPath = "C:\Users\dhwin\ActuAlte M1\arduino-brisumi-satoshi-real-system\keys\preprod.payment.cborHex.txt"
$Url = 'http://localhost:4002/transfer'
$OutPath = Join-Path $env:TEMP 'cardano_transfer_direct.json'

if (-not (Test-Path -LiteralPath $KeyPath)) { throw "Missing key: $KeyPath" }
$cbor = (Get-Content -LiteralPath $KeyPath -Raw).Trim()

$body = [pscustomobject]@{
  fromAddress    = $FromAddr
  toAddress      = $ToAddr
  amountLovelace = $AmountLovelace
  skeyCbor       = $cbor
}

$body | ConvertTo-Json -Compress | Set-Content -LiteralPath $OutPath -Encoding UTF8
Write-Host "Prepared direct body at: $OutPath"

try {
  $resp = Invoke-RestMethod -Uri $Url -Method Post -ContentType 'application/json' -InFile $OutPath -TimeoutSec 180
  Write-Host 'Response:' -ForegroundColor Cyan
  $resp | ConvertTo-Json -Depth 6
} catch {
  Write-Host 'Request failed:' -ForegroundColor Red
  $_.Exception.Message
  if ($_.ErrorDetails) { $_.ErrorDetails.Message }
  throw
}
