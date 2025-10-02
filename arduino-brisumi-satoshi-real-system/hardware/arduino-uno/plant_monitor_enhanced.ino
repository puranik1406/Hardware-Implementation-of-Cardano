/*
 * Arduino Uno #1 - Enhanced Payment Trigger with Plant Monitoring
 * Hardware:
 *   - Button on Pin 2 (Payment Trigger) - EXISTING
 *   - Soil Moisture Sensor:
 *       VCC → 5V
 *       GND → GND
 *       DO  → Pin 3 (Digital threshold)
 *       AO  → A0 (Analog reading)
 * 
 * Purpose: 
 *   1. Trigger Cardano payments when button pressed (UNCHANGED)
 *   2. Monitor soil moisture and send plant health data (NEW)
 */

// Pin Definitions
const int BUTTON_PIN = 2;           // Payment trigger button (EXISTING)
const int MOISTURE_DIGITAL_PIN = 3; // Soil moisture digital output (NEW)
const int MOISTURE_ANALOG_PIN = A0; // Soil moisture analog input (NEW)

// State Variables
volatile bool buttonPressed = false;
bool waitingForResponse = false;

// Plant Monitoring Variables
int moistureRaw = 0;          // Raw ADC value (0-1023)
int moisturePercent = 0;      // Converted to percentage
bool isDry = false;           // Digital threshold status
unsigned long lastPlantCheck = 0;
const unsigned long PLANT_CHECK_INTERVAL = 60000; // Check every 60 seconds

void setup() {
  // Initialize button pin (EXISTING)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Initialize soil moisture sensor pins (NEW)
  pinMode(MOISTURE_DIGITAL_PIN, INPUT);
  pinMode(MOISTURE_ANALOG_PIN, INPUT);
  
  // Attach interrupt for button (EXISTING)
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonISR, FALLING);
  
  // Start serial communication
  Serial.begin(9600);
  
  Serial.println("READY");
  Serial.println("Arduino Enhanced: Payment Trigger + Plant Monitor");
  Serial.println("Plant Type: Aloe Vera");
  Serial.println("Sensors: Button (Pin2), Moisture (A0, Pin3)");
  
  // Initial plant reading
  readPlantSensors();
}

void buttonISR() {
  // Simple debounce - set flag (EXISTING)
  if (!waitingForResponse) {
    buttonPressed = true;
  }
}

void loop() {
  // Handle button press for payment (EXISTING - UNCHANGED)
  if (buttonPressed && !waitingForResponse) {
    buttonPressed = false;
    triggerPayment();
  }
  
  // Periodic plant health monitoring (NEW)
  if (millis() - lastPlantCheck > PLANT_CHECK_INTERVAL) {
    lastPlantCheck = millis();
    sendPlantHealthData();
  }
  
  // Listen for responses from PC (EXISTING)
  if (Serial.available() > 0) {
    String response = Serial.readStringUntil('\n');
    response.trim();
    handleResponse(response);
  }
  
  delay(10);
}

void readPlantSensors() {
  // Read analog moisture sensor (0-1023)
  moistureRaw = analogRead(MOISTURE_ANALOG_PIN);
  
  // Convert to percentage (0% = dry, 100% = wet)
  // Calibration: dry soil ~800-1023, wet soil ~200-400
  moisturePercent = map(moistureRaw, 1023, 200, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);
  
  // Read digital threshold (LOW = dry, HIGH = wet)
  isDry = (digitalRead(MOISTURE_DIGITAL_PIN) == LOW);
}

void sendPlantHealthData() {
  // Read all sensors
  readPlantSensors();
  
  // Mock temperature and humidity (replace with real sensors if available)
  float temperature = 24.5;  // Mock: 24.5°C
  int humidity = 55;         // Mock: 55%
  
  // Send plant data to PC
  Serial.println("PLANT_HEALTH_DATA");
  Serial.print("PLANT_TYPE:Aloe Vera");
  Serial.println();
  Serial.print("MOISTURE_RAW:");
  Serial.println(moistureRaw);
  Serial.print("MOISTURE_PERCENT:");
  Serial.println(moisturePercent);
  Serial.print("MOISTURE_THRESHOLD:");
  Serial.println(isDry ? "DRY" : "OK");
  Serial.print("TEMPERATURE:");
  Serial.println(temperature, 1);
  Serial.print("HUMIDITY:");
  Serial.println(humidity);
  Serial.println("END_PLANT_DATA");
  
  // Local status output
  Serial.print("[PLANT] Moisture: ");
  Serial.print(moisturePercent);
  Serial.print("% (");
  Serial.print(moistureRaw);
  Serial.print("), Status: ");
  
  if (moisturePercent >= 60 && moisturePercent <= 70) {
    Serial.println("OPTIMAL ✓");
  } else if (moisturePercent < 50) {
    Serial.println("DRY - Water needed!");
  } else if (moisturePercent > 70) {
    Serial.println("WET - Risk of overwatering");
  } else {
    Serial.println("OK");
  }
}

void triggerPayment() {
  // EXISTING PAYMENT TRIGGER - UNCHANGED
  // Send payment trigger command to PC
  Serial.println("TRIGGER_PAYMENT");
  Serial.println("FROM_AGENT:satoshi_alpha_001");
  Serial.println("TO_AGENT:satoshi_beta_002");
  Serial.println("AMOUNT:1");
  Serial.println("EMOTION:I am so happy and excited about this amazing blockchain transaction!");
  
  // Include current plant status with payment (NEW ENHANCEMENT)
  readPlantSensors();
  Serial.print("PLANT_STATUS:Moisture=");
  Serial.print(moisturePercent);
  Serial.println("%");
  
  Serial.println("END_COMMAND");
  
  waitingForResponse = true;
}

void handleResponse(String response) {
  // Handle transaction responses (EXISTING)
  if (response.startsWith("TX:") || response == "REJECTED" || response == "ERROR") {
    waitingForResponse = false;
    
    // If transaction successful, also log plant data
    if (response.startsWith("TX:")) {
      Serial.print("[INFO] Transaction completed. Plant moisture: ");
      Serial.print(moisturePercent);
      Serial.println("%");
    }
  }
  
  // Handle plant monitoring commands (NEW)
  if (response == "REQUEST_PLANT_DATA") {
    sendPlantHealthData();
  }
  
  if (response == "WATER_PLANT") {
    Serial.println("[ALERT] Manual watering requested!");
    // Could trigger a relay/pump here in future
  }
}
