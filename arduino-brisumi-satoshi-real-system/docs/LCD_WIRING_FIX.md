# 🔌 LCD Display Wiring Guide - FIXED (JHD 162A)

## ❌ PROBLEM IDENTIFIED - WRONG LCD TYPE!

**Your LCD (JHD 162A from photo) is a PARALLEL LCD, NOT an I2C LCD!**

This is why you see garbled characters (dots/squares):
- ❌ Using `LiquidCrystal_I2C` library with a PARALLEL LCD
- ❌ I2C code sends I2C protocol, but LCD expects parallel data
- ❌ **Completely incompatible** - they speak different languages!

### What You're Seeing:
- LCD backlight: ✅ Working (green glow)
- LCD receiving data: ✅ Working (something appears)  
- LCD showing correct text: ❌ FAIL (garbled because wrong protocol)

### Current (Wrong) Wiring:
- ❌ SDA → Pin 2 (Wrong for both I2C and parallel!)
- ❌ SCL → GND (Wrong!)
- ❌ VCC → 3.5V (Should be 5V!)
- ✅ GND → GND (Correct)

## ✅ CORRECT WIRING FOR YOUR JHD 162A LCD (Parallel Mode)

Your LCD has **16 pins** (not 4 like I2C). You need to wire it in parallel mode:

### Standard 16x2 Parallel LCD Pinout:

```
LCD Pin → Arduino Uno Pin
─────────────────────────────
VSS (Pin 1, GND)  → GND
VDD (Pin 2, 5V)   → 5V
V0  (Pin 3, Contrast) → Potentiometer center OR GND
RS  (Pin 4)       → Pin 12
RW  (Pin 5)       → GND (write-only mode)
E   (Pin 6)       → Pin 11
D0  (Pin 7)       → (not used in 4-bit mode)
D1  (Pin 8)       → (not used in 4-bit mode)
D2  (Pin 9)       → (not used in 4-bit mode)
D3  (Pin 10)      → (not used in 4-bit mode)
D4  (Pin 11)      → Pin 5
D5  (Pin 12)      → Pin 4
D6  (Pin 13)      → Pin 3
D7  (Pin 14)      → Pin 2
A   (Pin 15, Backlight+) → 5V (via 220Ω resistor)
K   (Pin 16, Backlight-) → GND
```

### Simplified (4-bit Mode - 6 wires + power):
```
LCD → Arduino
──────────────
VSS → GND
VDD → 5V
V0  → GND (or potentiometer for adjustable contrast)
RS  → Pin 12
RW  → GND
E   → Pin 11
D4  → Pin 5
D5  → Pin 4
D6  → Pin 3
D7  → Pin 2
A   → 5V (via 220Ω resistor for backlight)
K   → GND
```

---

## 📝 UPDATED ARDUINO CODE

**❌ DO NOT USE:** `transaction_display.ino` (I2C version - WRONG for your LCD!)

**✅ USE:** `transaction_display_direct.ino` (Parallel version - CORRECT!)

The new code uses `LiquidCrystal` library (built-in), not `LiquidCrystal_I2C`.

### Code Changes:
```cpp
// OLD (I2C - WRONG):
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

// NEW (Parallel - CORRECT):
#include <LiquidCrystal.h>
LiquidCrystal lcd(12, 11, 5, 4, 3, 2); // RS, E, D4, D5, D6, D7
```

---
D7   → Pin 2
A    → 5V (backlight +)
K    → GND (backlight -)
```

### Upload This Code (For Parallel LCD):
Use: `transaction_display_simple.ino` (New version without I2C)

---

## 🔧 QUICK FIX STEPS

### Option A: Fix the I2C Wiring (5 minutes)

1. **Disconnect Arduino from USB**
2. **Rewire LCD Module:**
   ```
   Remove: SDA from Pin 2 → Connect: SDA to A4
   Remove: SCL from GND  → Connect: SCL to A5
   Remove: VCC from 3.5V → Connect: VCC to 5V
   Keep: GND to GND
   ```
3. **Reconnect Arduino to USB**
4. **Upload:** `transaction_display.ino` (original code)
5. **Test:** Send `STATUS:LCD Ready` via Serial Monitor

### Option B: Switch to Parallel LCD (If you have one)

1. **Get a 16x2 LCD without I2C module** (plain LCD)
2. **Wire according to parallel wiring above**
3. **Upload:** `transaction_display_simple.ino`
4. **Test:** Send `TX:abc123def456` via Serial Monitor

---

## 🧪 Testing Your LCD

### Test 1: Check I2C Address (If using I2C)
```cpp
// Upload this to Arduino to find I2C address
#include <Wire.h>

void setup() {
  Serial.begin(9600);
  Wire.begin();
  Serial.println("Scanning I2C devices...");
  
  byte count = 0;
  for (byte i = 8; i < 120; i++) {
    Wire.beginTransmission(i);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      if (i < 16) Serial.print("0");
      Serial.println(i, HEX);
      count++;
    }
  }
  
  if (count == 0) {
    Serial.println("No I2C devices found!");
    Serial.println("Check wiring: SDA=A4, SCL=A5");
  }
}

void loop() {}
```

### Test 2: Serial Monitor Test
1. Open Arduino IDE Serial Monitor
2. Set baud rate to **9600**
3. Send these commands:
   ```
   STATUS:Test Message
   TX:abc123def456ghi789
   ERROR:Test Error
   CLEAR
   ```

### Test 3: From Arduino Bridge
Once Arduino Bridge is running:
```powershell
# Test sending to LCD
curl -X POST http://localhost:5001/trigger
```

---

## 📊 Troubleshooting

### LCD Shows Nothing:
- ❌ **Wrong wiring** → Fix SDA/SCL to A4/A5
- ❌ **Wrong voltage** → Use 5V not 3.5V
- ❌ **Wrong I2C address** → Try 0x27 or 0x3F in code
- ❌ **Contrast too low** → Adjust potentiometer on LCD

### LCD Shows Garbage Characters:
- ❌ **Wrong baud rate** → Must be 9600
- ❌ **Loose connections** → Check all wires
- ❌ **Power issues** → Use 5V stable power

### Serial Communication Works But LCD Doesn't:
- ❌ **I2C not initialized** → Check Wire.begin() in code
- ❌ **Wrong LCD address** → Run I2C scanner test
- ❌ **Faulty LCD module** → Test with simple blink code

---

## 🎯 RECOMMENDED ACTION NOW

**IMMEDIATE FIX (2 minutes):**

1. Stop Arduino Bridge: `Ctrl+C` in terminal
2. Fix LCD wiring:
   ```
   SDA: Pin 2  → A4
   SCL: GND    → A5
   VCC: 3.5V   → 5V
   ```
3. Re-upload `transaction_display.ino` to Arduino COM3
4. Restart Arduino Bridge
5. Test transaction again

**This will fix the issue!**

---

## 📝 Current Wiring Issues Explained

### Why SCL to GND Doesn't Work:
- SCL = Serial Clock Line (must be active signal)
- GND = Ground (0V, no signal)
- **SCL needs to pulse HIGH/LOW** for I2C communication
- Connecting to GND means **always LOW** = no communication

### Why Pin 2 for SDA Doesn't Work:
- I2C on Arduino Uno uses **hardware pins A4/A5**
- Pin 2 is just a regular digital pin
- LiquidCrystal_I2C library **only works with A4/A5**
- **Software I2C is possible** but requires different library

### Why 3.5V is Risky:
- LCD modules expect **5V logic levels**
- 3.3V or 3.5V might work partially but **unreliable**
- Backlight may be dim or not work
- Risk of data corruption on I2C bus

---

## ✅ After Fixing - Verification

Run this command to verify:
```powershell
cd "C:\Users\dhwin\ActuAlte M1\arduino-brisumi-satoshi-real-system"
curl -X POST http://localhost:5001/trigger
```

**Expected Result:**
1. Arduino COM6: Button detected
2. Transaction processed
3. **Arduino COM3: TX hash displayed on LCD** ✅
4. Dashboard shows transaction

---

**Fix the wiring and everything will work!** 🚀
