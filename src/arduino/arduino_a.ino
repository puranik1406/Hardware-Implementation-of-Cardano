/*
 * Arduino A - Offer Trigger System
 * Triggers offers based on sensor data and displays transaction status
 * Compatible with Wokwi simulation
 */

#include <LiquidCrystal.h>

// LCD pins (adjust for your setup)
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// Sensor and button pins
const int sensorPin = A0;    // Analog sensor (potentiometer in simulation)
const int buttonPin = 8;     // Trigger button
const int ledPin = 13;       // Status LED

// Thresholds and states
const int triggerThreshold = 512;  // Sensor threshold for triggering offers
int lastButtonState = HIGH;
int currentButtonState = HIGH;
bool offerInProgress = false;
unsigned long lastTriggerTime = 0;
const unsigned long cooldownPeriod = 5000;  // 5 seconds cooldown

// Serial communication
String incomingData = "";
bool dataComplete = false;

// Display states
enum DisplayState {
  WAITING,
  TRIGGERED,
  OFFER_SENT,
  TRANSACTION_PENDING,
  COMPLETED,
  ERROR_STATE
};

DisplayState currentState = WAITING;
String currentOfferID = "";
String currentTxHash = "";

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.begin(16, 2);
  
  // Initialize pins
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  
  // Display startup message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Arduino A Ready");
  lcd.setCursor(0, 1);
  lcd.print("Cardano AI Agent");
  
  digitalWrite(ledPin, LOW);
  
  Serial.println("=================================");
  Serial.println("Arduino A - Offer Trigger System");
  Serial.println("=================================");
  Serial.println("Commands:");
  Serial.println("- OFFER:amount:product - Manual offer trigger");
  Serial.println("- STATUS:offer_id - Check offer status");
  Serial.println("- TX:tx_hash - Transaction confirmed");
  Serial.println("- RESET - Reset system");
  Serial.println("=================================");
  
  delay(2000);
  updateDisplay();
}

void loop() {
  // Read sensor value
  int sensorValue = analogRead(sensorPin);
  
  // Read button state
  currentButtonState = digitalRead(buttonPin);
  
  // Check for sensor trigger
  if (sensorValue > triggerThreshold && !offerInProgress) {
    unsigned long currentTime = millis();
    if (currentTime - lastTriggerTime > cooldownPeriod) {
      triggerOffer("sensor", sensorValue);
      lastTriggerTime = currentTime;
    }
  }
  
  // Check for button press
  if (lastButtonState == HIGH && currentButtonState == LOW && !offerInProgress) {
    unsigned long currentTime = millis();
    if (currentTime - lastTriggerTime > cooldownPeriod) {
      triggerOffer("button", 100);
      lastTriggerTime = currentTime;
    }
  }
  lastButtonState = currentButtonState;
  
  // Handle serial communication
  handleSerial();
  
  // Update LED
  updateLED();
  
  delay(100);
}

void triggerOffer(String triggerType, int value) {
  offerInProgress = true;
  currentState = TRIGGERED;
  
  // Calculate offer amount based on sensor value
  float offerAmount = map(value, 0, 1023, 50, 200);
  String product = "Arduino Sensor Data";
  
  // Generate offer ID
  currentOfferID = String(millis());
  
  // Send offer trigger to Agent A via serial
  String offerData = "TRIGGER:";
  offerData += triggerType + ":";
  offerData += String(offerAmount, 1) + ":";
  offerData += product + ":";
  offerData += currentOfferID;
  
  Serial.println(offerData);
  Serial.println("Offer triggered - Amount: " + String(offerAmount, 1) + " ADA");
  
  currentState = OFFER_SENT;
  updateDisplay();
  
  // Auto-advance to waiting after a timeout
  setTimeout(10000, WAITING);
}

void handleSerial() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n') {
      dataComplete = true;
    } else {
      incomingData += inChar;
    }
  }
  
  if (dataComplete) {
    processSerialCommand(incomingData);
    incomingData = "";
    dataComplete = false;
  }
}

void processSerialCommand(String command) {
  command.trim();
  Serial.println("Received: " + command);
  
  if (command.startsWith("OFFER_ACCEPTED:")) {
    // Extract offer ID and transaction hash
    int firstColon = command.indexOf(':');
    int secondColon = command.indexOf(':', firstColon + 1);
    
    String offerID = command.substring(firstColon + 1, secondColon);
    String txHash = command.substring(secondColon + 1);
    
    if (offerID == currentOfferID) {
      currentTxHash = txHash;
      currentState = TRANSACTION_PENDING;
      Serial.println("Offer accepted! Transaction: " + txHash);
      updateDisplay();
    }
  }
  else if (command.startsWith("OFFER_REJECTED:")) {
    String offerID = command.substring(command.indexOf(':') + 1);
    
    if (offerID == currentOfferID) {
      currentState = ERROR_STATE;
      Serial.println("Offer rejected");
      updateDisplay();
      setTimeout(3000, WAITING);
    }
  }
  else if (command.startsWith("TX_CONFIRMED:")) {
    String txHash = command.substring(command.indexOf(':') + 1);
    
    if (txHash == currentTxHash) {
      currentState = COMPLETED;
      Serial.println("Transaction confirmed! " + txHash);
      updateDisplay();
      setTimeout(5000, WAITING);
    }
  }
  else if (command == "RESET") {
    resetSystem();
  }
  else if (command.startsWith("STATUS:")) {
    Serial.println("Current State: " + getStateName(currentState));
    Serial.println("Offer ID: " + currentOfferID);
    Serial.println("TX Hash: " + currentTxHash);
  }
  else {
    Serial.println("Unknown command: " + command);
  }
}

void updateDisplay() {
  lcd.clear();
  
  switch (currentState) {
    case WAITING:
      lcd.setCursor(0, 0);
      lcd.print("Ready for Offers");
      lcd.setCursor(0, 1);
      lcd.print("Press button/sensor");
      offerInProgress = false;
      currentOfferID = "";
      currentTxHash = "";
      break;
      
    case TRIGGERED:
      lcd.setCursor(0, 0);
      lcd.print("Triggering...");
      lcd.setCursor(0, 1);
      lcd.print("Creating offer");
      break;
      
    case OFFER_SENT:
      lcd.setCursor(0, 0);
      lcd.print("Offer Sent");
      lcd.setCursor(0, 1);
      lcd.print("ID: " + currentOfferID.substring(0, 10));
      break;
      
    case TRANSACTION_PENDING:
      lcd.setCursor(0, 0);
      lcd.print("TX Pending...");
      lcd.setCursor(0, 1);
      lcd.print(currentTxHash.substring(0, 16));
      break;
      
    case COMPLETED:
      lcd.setCursor(0, 0);
      lcd.print("✓ COMPLETED");
      lcd.setCursor(0, 1);
      lcd.print("TX: " + currentTxHash.substring(0, 12));
      break;
      
    case ERROR_STATE:
      lcd.setCursor(0, 0);
      lcd.print("✗ REJECTED");
      lcd.setCursor(0, 1);
      lcd.print("Try again later");
      break;
  }
}

void updateLED() {
  switch (currentState) {
    case WAITING:
      digitalWrite(ledPin, LOW);
      break;
      
    case TRIGGERED:
    case OFFER_SENT:
      // Blink LED
      digitalWrite(ledPin, (millis() / 500) % 2);
      break;
      
    case TRANSACTION_PENDING:
      // Fast blink
      digitalWrite(ledPin, (millis() / 200) % 2);
      break;
      
    case COMPLETED:
      digitalWrite(ledPin, HIGH);
      break;
      
    case ERROR_STATE:
      // Slow blink
      digitalWrite(ledPin, (millis() / 1000) % 2);
      break;
  }
}

void setTimeout(unsigned long duration, DisplayState nextState) {
  // Simple timeout implementation
  static unsigned long timeoutStart = 0;
  static DisplayState timeoutNextState = WAITING;
  static bool timeoutActive = false;
  
  if (!timeoutActive) {
    timeoutStart = millis();
    timeoutNextState = nextState;
    timeoutActive = true;
  }
  
  if (millis() - timeoutStart > duration) {
    currentState = timeoutNextState;
    timeoutActive = false;
    updateDisplay();
  }
}

void resetSystem() {
  currentState = WAITING;
  offerInProgress = false;
  currentOfferID = "";
  currentTxHash = "";
  
  Serial.println("System reset");
  updateDisplay();
}

String getStateName(DisplayState state) {
  switch (state) {
    case WAITING: return "WAITING";
    case TRIGGERED: return "TRIGGERED";
    case OFFER_SENT: return "OFFER_SENT";
    case TRANSACTION_PENDING: return "TRANSACTION_PENDING";
    case COMPLETED: return "COMPLETED";
    case ERROR_STATE: return "ERROR_STATE";
    default: return "UNKNOWN";
  }
}

// Additional helper functions for sensor calibration
void calibrateSensor() {
  Serial.println("Calibrating sensor...");
  
  int minVal = 1023;
  int maxVal = 0;
  
  for (int i = 0; i < 100; i++) {
    int val = analogRead(sensorPin);
    if (val < minVal) minVal = val;
    if (val > maxVal) maxVal = val;
    delay(50);
  }
  
  Serial.println("Sensor range: " + String(minVal) + " - " + String(maxVal));
}