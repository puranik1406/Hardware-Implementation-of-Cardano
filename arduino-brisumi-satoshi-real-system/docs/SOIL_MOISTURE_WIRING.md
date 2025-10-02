# 🔌 Soil Moisture Sensor Wiring Guide

## Components
- **Arduino Uno** (COM6)
- **Capacitive/Resistive Soil Moisture Sensor**
- **Jumper Wires**

## Sensor Pin Descriptions

| Sensor Pin | Function | Voltage Range |
|------------|----------|---------------|
| **VCC** | Power Input | 3.3V - 5V DC |
| **GND** | Ground | Ground |
| **DO** | Digital Output | HIGH/LOW threshold |
| **AO** | Analog Output | 0-1023 ADC value |

## Wiring Diagram

```
┌─────────────────────────────────────┐
│   Soil Moisture Sensor              │
│                                     │
│  VCC   GND   DO    AO               │
│   │     │     │     │               │
└───┼─────┼─────┼─────┼───────────────┘
    │     │     │     │
    │     │     │     │
    │     │     │     └────────────┐
    │     │     │                  │
    │     │     └──────────┐       │
    │     │                │       │
    │     └────────┐       │       │
    │              │       │       │
┌───┼──────────────┼───────┼───────┼───────┐
│   │              │       │       │       │
│  5V            GND     Pin3     A0      │
│                                         │
│         Arduino Uno (COM6)              │
│                                         │
│  [Also connected:]                      │
│  - Button on Pin 2 (Payment Trigger)   │
│  - USB to PC for Serial                │
└─────────────────────────────────────────┘
```

## Step-by-Step Connection

### 1. Power Connections
```
Sensor VCC  →  Arduino 5V pin
Sensor GND  →  Arduino GND pin
```
⚠️ **Important**: Ensure 5V supply is stable. If sensor is 3.3V only, use 3.3V pin instead.

### 2. Digital Output (Threshold)
```
Sensor DO   →  Arduino Digital Pin 3
```
- **Purpose**: Simple dry/wet detection
- **Output**: HIGH when wet, LOW when dry (or vice versa, check sensor)
- **Adjustable**: Most sensors have a potentiometer to set threshold

### 3. Analog Output (Precise Reading)
```
Sensor AO   →  Arduino Analog Pin A0
```
- **Purpose**: Precise moisture measurement
- **Range**: 0-1023 (10-bit ADC)
- **Calibration**: 
  - Dry soil: ~800-1023
  - Moist soil: ~400-600
  - Wet soil: ~200-400

## Complete Pin Assignment Table

| Arduino Pin | Connection | Purpose |
|-------------|------------|---------|
| **Pin 2** | Button (existing) | Payment trigger |
| **Pin 3** | Moisture DO | Digital threshold |
| **A0** | Moisture AO | Analog reading |
| **5V** | Moisture VCC | Sensor power |
| **GND** | Moisture GND + Button GND | Ground |

## Calibration Procedure

### 1. Dry Soil Calibration
1. Remove sensor from soil
2. Wipe probe clean and dry
3. Upload Arduino sketch
4. Open Serial Monitor (9600 baud)
5. Note the ADC value (should be ~900-1023)

### 2. Wet Soil Calibration
1. Insert sensor in very wet soil (or glass of water)
2. Wait 10 seconds
3. Note the ADC value (should be ~200-300)

### 3. Update Code
In `plant_monitor_enhanced.ino`, adjust the `map()` function:
```cpp
// Replace with your calibrated values
moisturePercent = map(moistureRaw, 1023, 200, 0, 100);
//                                  ^^^^  ^^^
//                                  DRY   WET
```

## Testing Steps

### 1. Hardware Check
```
✓ VCC connected to 5V
✓ GND connected to GND
✓ DO connected to Pin 3
✓ AO connected to A0
✓ Button still on Pin 2 (existing)
```

### 2. Upload Sketch
1. Open Arduino IDE
2. Open `plant_monitor_enhanced.ino`
3. Select Board: Arduino Uno
4. Select Port: COM6
5. Upload

### 3. Verify Serial Output
Open Serial Monitor, you should see:
```
READY
Arduino Enhanced: Payment Trigger + Plant Monitor
Plant Type: Aloe Vera
Sensors: Button (Pin2), Moisture (A0, Pin3)
[PLANT] Moisture: 65% (350), Status: OPTIMAL ✓
```

### 4. Test Moisture Reading
- Dry: Remove from soil → should show 0-20%
- Wet: Insert in water → should show 80-100%
- Optimal: In moist soil → should show 60-70%

## Troubleshooting

### Problem: Always reads 0% or 100%
**Solution**: Check wiring, especially VCC and GND

### Problem: Random/unstable readings
**Solution**: 
- Add 10µF capacitor between VCC and GND
- Use shorter wires
- Keep away from other electronics

### Problem: Digital output (DO) not working
**Solution**: Adjust potentiometer on sensor module

### Problem: Analog readings stuck at 1023
**Solution**: Check AO pin connection to A0

## Safety Notes

⚠️ **Do not leave sensor continuously in soil**
- Corrosion can occur over time
- For permanent installation, use stainless steel probe
- Consider capacitive sensor (no exposed metal)

⚠️ **Current sensor is for Arduino #1 only**
- Arduino #2 (COM3) is for LCD display only
- Do not mix the two Arduino boards

## Expected Output in Serial Monitor

```
PLANT_HEALTH_DATA
PLANT_TYPE:Aloe Vera
MOISTURE_RAW:350
MOISTURE_PERCENT:65
MOISTURE_THRESHOLD:OK
TEMPERATURE:24.5
HUMIDITY:55
END_PLANT_DATA
[PLANT] Moisture: 65% (350), Status: OPTIMAL ✓
```

## Integration with Existing System

✅ **Existing functionality preserved:**
- Button on Pin 2 triggers Cardano payment (unchanged)
- Transaction hash displayed on Arduino #2 LCD (unchanged)
- Emotion AI approval (unchanged)

✅ **New functionality added:**
- Soil moisture monitoring every 60 seconds
- Plant health data sent to Sokosumi MCP
- Reports saved in `plant_reports/` folder
- Manual plant data request: Send "REQUEST_PLANT_DATA" via Serial

## Next Steps

1. ✅ Wire sensor according to diagram above
2. ✅ Upload `plant_monitor_enhanced.ino` to Arduino #1
3. ✅ Calibrate sensor (dry and wet readings)
4. ✅ Test with Serial Monitor
5. ✅ Run Node.js arduino-bridge (next step in main system)
6. ✅ Test payment button (ensure still works)
7. ✅ Verify LCD displays transaction hash (Arduino #2)
8. ✅ Check plant reports are generated
