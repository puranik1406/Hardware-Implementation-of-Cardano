# 🔍 LCD Troubleshooting Guide - Black Dots/No Display

## 📸 What You're Seeing (Photo Analysis)

**Symptom:** Black/dark dots at the top of LCD screen, no readable text
- ✅ LCD has power (backlight is on - green glow)
- ✅ Arduino is sending data (logs show successful writes)
- ❌ No readable text visible (garbled/dots/squares)

## 🎯 Root Cause Analysis

### Issue #1: **CONTRAST TOO HIGH** (Most Common!)

The V0 pin controls LCD contrast. If it's:
- **Floating (not connected):** Random contrast, usually too high → BLACK SQUARES
- **Connected to 5V:** Maximum contrast → COMPLETELY BLACK
- **Not adjusted properly:** Partial visibility

**SOLUTION:** Connect V0 pin (LCD Pin 3) to **GND** for maximum brightness (lowest contrast).

### Issue #2: **Wrong LCD Library/Protocol**

Your original code used I2C library (`LiquidCrystal_I2C`) with a **parallel LCD**.
- I2C sends serial data on 2 wires (SDA/SCL)
- Your LCD expects parallel data on 6 wires (RS, E, D4-D7)
- Result: Garbled characters

**SOLUTION:** Use `LiquidCrystal` library (parallel mode).

---

## ✅ STEP-BY-STEP FIX

### Step 1: Verify LCD Type

Your LCD: **JHD 162A** (visible in photo)
- Type: **16x2 Character LCD** (parallel interface)
- Pins: **16 pins** (not 4-pin I2C module!)
- Protocol: **HD44780 compatible** (standard parallel)

### Step 2: CORRECT Wiring (6 Data Pins + Power)

```
LCD Pin → Arduino Uno Pin
─────────────────────────────
1  VSS  → GND
2  VDD  → 5V
3  V0   → GND ⚠️ CRITICAL! (or potentiometer center)
4  RS   → Pin 12
5  RW   → GND (write mode)
6  E    → Pin 11
7  D0   → (not used)
8  D1   → (not used)
9  D2   → (not used)
10 D3   → (not used)
11 D4   → Pin 5
12 D5   → Pin 4
13 D6   → Pin 3
14 D7   → Pin 2
15 A    → 5V (via 220Ω resistor for backlight)
16 K    → GND
```

**⚠️ MOST IMPORTANT:** Pin 3 (V0/VEE) - This controls contrast!
- Try connecting to **GND first** (maximum brightness)
- If text is too bright/washed out, use a 10kΩ potentiometer:
  - Pot end 1 → 5V
  - Pot end 2 → GND  
  - Pot center → LCD Pin 3 (V0)

### Step 3: Upload Minimal Test Code

**File:** `lcd_minimal_test.ino`

This code will:
1. Display "HELLO WORLD!" on line 1
2. Display "Arduino Test 123" on line 2
3. Blink an asterisk to show it's alive

**Expected Result:** You should see clear text immediately after upload.

### Step 4: Test With Serial Monitor

1. Open Arduino IDE → Tools → Serial Monitor
2. Set baud rate to **9600**
3. Type: `TX:test123` and press Enter
4. LCD should clear and show "Received:" and "test123"

---

## 🔧 Quick Hardware Checks

### Check 1: Power
```
Multimeter Test:
- Measure between VDD (LCD Pin 2) and VSS (LCD Pin 1)
- Should read: 5V ±0.25V
- If not 5V: Check Arduino 5V pin and wiring
```

### Check 2: Contrast (V0 Pin)
```
LCD Pin 3 (V0/VEE):
✅ Connected to GND: Maximum brightness (try this first!)
✅ Connected to potentiometer: Adjustable
❌ Floating (not connected): Random/too high contrast → BLACK SQUARES
❌ Connected to 5V: Completely black screen
```

### Check 3: Data Pins Continuity
```
Test with multimeter (continuity mode):
RS (LCD Pin 4)  ↔ Arduino Pin 12
E  (LCD Pin 6)  ↔ Arduino Pin 11
D4 (LCD Pin 11) ↔ Arduino Pin 5
D5 (LCD Pin 12) ↔ Arduino Pin 4
D6 (LCD Pin 13) ↔ Arduino Pin 3
D7 (LCD Pin 14) ↔ Arduino Pin 2
```

---

## 📊 Diagnostic Tests

### Test 1: Minimal Code (No Serial)
Upload `lcd_minimal_test.ino` → Should see "HELLO WORLD!" immediately

### Test 2: Contrast Adjustment
If you see black squares:
1. Disconnect V0 (Pin 3) completely
2. Connect V0 to GND
3. If still black, connect V0 to potentiometer

### Test 3: Simple Character Test
Add this to your code:
```cpp
void loop() {
  lcd.clear();
  lcd.print("ABCDEFGHIJKLMNOP");
  lcd.setCursor(0, 1);
  lcd.print("0123456789!@#$%^");
  delay(1000);
}
```

Should display full alphabet and numbers clearly.

---

## 🎯 Expected Behavior After Fix

### On Power Up (Immediate):
```
┌────────────────┐
│HELLO WORLD!    │
│Arduino Test 123│
└────────────────┘
```

### After Arduino Bridge Sends TX:
```
┌────────────────┐
│New TX:         │
│4e5eec86a76ed61│
└────────────────┘
```

---

## ⚠️ Common Mistakes

1. **V0 pin floating** → Black squares (YOUR ISSUE!)
2. **Using I2C library with parallel LCD** → Garbled text
3. **Wrong pin mapping** → No display or wrong characters
4. **RW pin not connected to GND** → LCD in read mode, no display
5. **3.3V instead of 5V** → Dim or no display

---

## 🚀 Quick Fix Summary

**If you see BLACK DOTS/SQUARES:**

1. ✅ Connect LCD Pin 3 (V0) to **GND** directly
2. ✅ Upload `lcd_minimal_test.ino`
3. ✅ Check Serial Monitor for "LCD Test - Text displayed!"
4. ✅ Look at LCD - should see "HELLO WORLD!"

**If still nothing:**
- Check VDD = 5V (not 3.3V)
- Verify all 6 data pins are connected correctly
- Try different Arduino pins (might be damaged pins)
- Test LCD with known-good Arduino code

---

## 📞 Next Steps

1. **Upload** `lcd_minimal_test.ino` to Arduino #2 (COM3)
2. **Connect** V0 (Pin 3) to GND
3. **Power** Arduino and look for "HELLO WORLD!"
4. **Report back** what you see on the LCD

If you see clear text, then we'll move to the transaction display code.
If you still see dots/squares, we'll check hardware connections.
