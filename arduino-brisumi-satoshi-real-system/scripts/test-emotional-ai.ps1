# Quick Start Script for Emotional AI + Hardware Testing
# Run this after Docker Compose is running

Write-Host "🚀 Starting Emotional AI + Cardano Hardware System..." -ForegroundColor Cyan
Write-Host ""

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test 1: Check Emotional AI Service
Write-Host "`n✅ Test 1: Checking Emotional AI Service..." -ForegroundColor Green
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:7002/health" -Method GET
    Write-Host "   Emotional AI: ONLINE ✓" -ForegroundColor Green
} catch {
    Write-Host "   Emotional AI: OFFLINE ✗" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# Test 2: Positive Emotion Test
Write-Host "`n✅ Test 2: Testing Positive Emotion (Should APPROVE)..." -ForegroundColor Green
$positiveTest = @{
    text = "I am so happy and excited about this amazing blockchain transaction! This is wonderful!"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:7002/api/check" -Method POST -ContentType "application/json" -Body $positiveTest
    Write-Host "   Approved: $($result.approved)" -ForegroundColor $(if($result.approved){"Green"}else{"Red"})
    Write-Host "   Positive: $($result.positiveScore)%" -ForegroundColor Cyan
    Write-Host "   Negative: $($result.negativeScore)%" -ForegroundColor Cyan
    Write-Host "   Reason: $($result.reason)" -ForegroundColor Gray
} catch {
    Write-Host "   Test FAILED: $_" -ForegroundColor Red
}

# Test 3: Negative Emotion Test
Write-Host "`n✅ Test 3: Testing Negative Emotion (Should REJECT)..." -ForegroundColor Green
$negativeTest = @{
    text = "I am very angry and frustrated about this terrible situation. This is awful!"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:7002/api/check" -Method POST -ContentType "application/json" -Body $negativeTest
    Write-Host "   Approved: $($result.approved)" -ForegroundColor $(if($result.approved){"Red"}else{"Green"})
    Write-Host "   Positive: $($result.positiveScore)%" -ForegroundColor Cyan
    Write-Host "   Negative: $($result.negativeScore)%" -ForegroundColor Cyan
    Write-Host "   Reason: $($result.reason)" -ForegroundColor Gray
} catch {
    Write-Host "   Test FAILED: $_" -ForegroundColor Red
}

# Test 4: Check Arduino Bridge
Write-Host "`n✅ Test 4: Checking Arduino Bridge Service..." -ForegroundColor Green
try {
    $bridgeHealth = Invoke-RestMethod -Uri "http://localhost:5001/health" -Method GET
    Write-Host "   Arduino Bridge: ONLINE ✓" -ForegroundColor Green
} catch {
    Write-Host "   Arduino Bridge: OFFLINE ✗" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# Test 5: Full Integration Test with Positive Emotion
Write-Host "`n✅ Test 5: Full Integration Test (Positive Emotion → Payment)..." -ForegroundColor Green
$emotionContext = @{
    text = "I am feeling great and confident about this payment!"
} | ConvertTo-Json

try {
    # Set emotional context
    Invoke-RestMethod -Uri "http://localhost:5001/emotion" -Method POST -ContentType "application/json" -Body $emotionContext | Out-Null
    Write-Host "   Emotional context set ✓" -ForegroundColor Green
    
    # Trigger payment
    Write-Host "   Triggering payment simulation..." -ForegroundColor Yellow
    $paymentResult = Invoke-RestMethod -Uri "http://localhost:5001/simulate" -Method POST
    Write-Host "   Payment triggered ✓" -ForegroundColor Green
    Write-Host "   Check logs for transaction details" -ForegroundColor Gray
} catch {
    Write-Host "   Integration test FAILED: $_" -ForegroundColor Red
}

# Test 6: Full Integration Test with Negative Emotion
Write-Host "`n✅ Test 6: Full Integration Test (Negative Emotion → Should Reject)..." -ForegroundColor Green
$negativeContext = @{
    text = "I am very angry and do not want to proceed with this!"
} | ConvertTo-Json

try {
    # Set emotional context
    Invoke-RestMethod -Uri "http://localhost:5001/emotion" -Method POST -ContentType "application/json" -Body $negativeContext | Out-Null
    Write-Host "   Emotional context set ✓" -ForegroundColor Green
    
    # Try to trigger payment (should be rejected)
    Write-Host "   Attempting payment (should be rejected)..." -ForegroundColor Yellow
    $paymentResult = Invoke-RestMethod -Uri "http://localhost:5001/simulate" -Method POST
    Write-Host "   Check logs to confirm rejection" -ForegroundColor Gray
} catch {
    Write-Host "   Rejection test FAILED: $_" -ForegroundColor Red
}

# Summary
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ SYSTEM READY FOR HARDWARE TESTING!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Connect Arduino Uno #1 (Button Trigger) to COM6" -ForegroundColor White
Write-Host "   2. Connect Arduino Uno #2 (LCD Display) to COM3" -ForegroundColor White
Write-Host "   3. Upload Arduino sketches from hardware/ folder" -ForegroundColor White
Write-Host "   4. Press the button on Arduino #1 to trigger payment" -ForegroundColor White
Write-Host "   5. Watch LCD on Arduino #2 for transaction hash" -ForegroundColor White
Write-Host ""
Write-Host "📊 Monitor Services:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f emotion-ai" -ForegroundColor Gray
Write-Host "   docker-compose logs -f arduino-bridge" -ForegroundColor Gray
Write-Host "   docker-compose logs -f masumi-payment" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Open Dashboard:" -ForegroundColor Yellow
Write-Host "   http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
