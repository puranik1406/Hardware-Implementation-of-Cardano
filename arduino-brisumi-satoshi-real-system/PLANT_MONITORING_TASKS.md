# 🌱 Plant Health Monitoring Tasks - Aloe Vera System

## ✅ COMPLETED
- [x] Sokosumi MCP server cloned and configured
- [x] Sokosumi integration service created
- [x] Research report generator script created
- [x] All changes pushed to GitHub
- [x] Existing Cardano transaction system working (DO NOT MODIFY)
- [x] Arduino #2 LCD display code exists (COM3)

## 🚧 IN PROGRESS - Soil Moisture Sensor Integration

### Hardware Setup
- [ ] **Soil Moisture Sensor Wiring to Arduino #1 (COM6)**
  - VCC → 5V pin on Arduino
  - GND → GND pin on Arduino
  - DO (Digital Output) → Pin 3 on Arduino
  - AO (Analog Output) → A0 pin on Arduino

### Software Components to Add

#### 1. Arduino #1 - Enhanced with Soil Moisture (COM6)
- [ ] Add soil moisture reading on A0 (analog pin)
- [ ] Read digital threshold on Pin 3
- [ ] Keep existing button trigger on Pin 2 (DO NOT REMOVE)
- [ ] Send plant data with transaction trigger
- [ ] Format: `PLANT_DATA:moisture,temp,humidity`

#### 2. Sokosumi Plant Health Agent Integration
- [ ] Create plant health monitoring endpoint in arduino-bridge
- [ ] Endpoint: `POST /plant-health`
- [ ] Accept sensor data (moisture, temp, humidity)
- [ ] Send to Sokosumi MCP with plant context (Aloe Vera)
- [ ] Store reports in `plant_reports/` folder

#### 3. Report Storage System
- [ ] Create `plant_reports/` directory structure
  - `plant_reports/daily/` - Daily reports
  - `plant_reports/alerts/` - Critical alerts
  - `plant_reports/archive/` - Historical data
- [ ] Format: `aloe_vera_report_YYYYMMDD_HHMMSS.txt`
- [ ] Include: timestamp, sensor readings, Sokosumi AI analysis

### 📋 Integration Flow

```
┌─────────────────────┐
│ Arduino #1 (COM6)   │
│ - Button (Pin 2)    │ ──── Trigger Payment ────┐
│ - Moisture (A0)     │                           │
│ - Digital (Pin 3)   │                           ▼
│ - Temp/Humidity     │              ┌─────────────────────────┐
└─────────────────────┘              │   Arduino Bridge        │
                                     │   (Node.js Server)      │
┌─────────────────────┐              │  - Payment Trigger      │
│ Arduino #2 (COM3)   │ ◄── TX Hash ─│  - Plant Health Monitor │
│ - LCD Display       │              │  - Sokosumi Client      │
└─────────────────────┘              └─────────────────────────┘
                                                │
                                                ├─── Cardano TX ───►
                                                │
                                                └─── Sokosumi AI ───►
                                                     Plant Report
```

## 🎯 Test Plan with Mock Data

### Phase 1: Mock Sensor Data Test
```javascript
{
  "plant_type": "Aloe Vera",
  "moisture": 65,        // Mock: 65% moisture
  "temperature": 24,     // Mock: 24°C
  "humidity": 55,        // Mock: 55% humidity
  "light_level": "medium",
  "timestamp": "2025-10-02T10:30:00Z"
}
```

### Phase 2: Sokosumi Agent Test
- [ ] Test with mock data
- [ ] Verify report generation
- [ ] Check file storage
- [ ] Validate report content

### Phase 3: Arduino Integration Test
- [ ] Upload enhanced sketch to Arduino #1
- [ ] Verify sensor readings in Serial Monitor
- [ ] Test button trigger (existing functionality)
- [ ] Test plant data transmission
- [ ] Verify LCD display still works for transactions

## 🔧 Implementation Steps

### Step 1: Hardware Wiring ⚡
**Soil Moisture Sensor → Arduino Uno #1**
```
Sensor Pin  →  Arduino Pin  →  Description
──────────────────────────────────────────
VCC         →  5V           →  Power supply
GND         →  GND          →  Ground
DO          →  Digital Pin 3 → Digital threshold output
AO          →  Analog Pin A0 → Analog moisture reading (0-1023)
```

### Step 2: Arduino Code Enhancement
- [ ] Modify `button_trigger.ino`
- [ ] Add soil moisture reading function
- [ ] Keep button interrupt (Pin 2) unchanged
- [ ] Add plant data serialization

### Step 3: Arduino Bridge Enhancement
- [ ] Add plant health monitoring route
- [ ] Create Sokosumi client integration
- [ ] Add report storage logic
- [ ] Keep existing payment flow intact

### Step 4: Sokosumi MCP Setup
- [ ] Test Sokosumi API with mock data
- [ ] Configure plant health agent
- [ ] Set up report templates

## 🔒 CRITICAL - DO NOT MODIFY
- ❌ Don't change existing transaction trigger code
- ❌ Don't modify Cardano integration
- ❌ Don't alter LCD display transaction code
- ❌ Don't remove button interrupt on Pin 2
- ✅ Only ADD new sensor reading functionality
- ✅ Only ADD plant health monitoring endpoints

## 📝 File Structure
```
arduino-brisumi-satoshi-real-system/
├── hardware/
│   └── arduino-uno/
│       ├── button_trigger.ino            [MODIFY - Add sensors]
│       └── transaction_display.ino       [NO CHANGE]
├── backend/
│   ├── arduino-bridge/
│   │   └── src/
│   │       └── index.js                  [MODIFY - Add plant endpoint]
│   └── sokosumi-integration/             [NEW SERVICE]
│       └── src/
│           └── plant-health-monitor.js   [NEW]
├── plant_reports/                        [NEW FOLDER]
│   ├── daily/
│   ├── alerts/
│   └── archive/
└── Sokosumi-MCP/
    └── generate_actualte_report.py       [MODIFY for plant health]
```

## 🧪 Testing Checklist
- [ ] Existing button trigger still works
- [ ] Transaction flow unchanged
- [ ] LCD displays transaction hash
- [ ] Soil moisture sensor reads correctly
- [ ] Plant data sent to Sokosumi
- [ ] Reports generated and stored
- [ ] Mock data test passes
- [ ] Real sensor test passes

## 📊 Expected Output
**Plant Health Report Example:**
```
========================================
Aloe Vera Health Report
Generated: 2025-10-02 10:30:00
========================================

SENSOR READINGS:
- Soil Moisture: 65% ✓ Optimal
- Temperature: 24°C ✓ Ideal
- Humidity: 55% ✓ Good

AI ANALYSIS (Sokosumi):
Your Aloe Vera plant is in excellent condition.
Moisture level is optimal for desert plants.
Temperature is within ideal range (18-27°C).
Recommendations:
- Continue current watering schedule
- Ensure good drainage
- Monitor for any leaf discoloration

NEXT WATERING: In 5 days
HEALTH STATUS: Excellent ✓
========================================
```

## 🚀 Next Actions
1. Wire soil moisture sensor to Arduino #1
2. Create mock data test script
3. Enhance Arduino code with sensor reading
4. Add plant health endpoint to arduino-bridge
5. Test with mock data before real sensors
6. Verify existing transaction flow still works
