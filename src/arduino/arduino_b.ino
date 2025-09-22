/*
 * Arduino B - Transaction Display System
 * Displays transaction confirmations and seller responses
 * Compatible with Wokwi simulation
 */

#include <LiquidCrystal.h>

// LCD pins (adjust for your setup)
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// LED pins for status indication
const int greenLED = 9;    // Confirmed transactions
const int redLED = 10;     // Rejected offers
const int blueLED = 6;     // Processing

// Button for manual acknowledgment
const int ackButton = 8;
int lastButtonState = HIGH;

// Serial communication
String incomingData = "";
bool dataComplete = false;

// Display states
enum DisplayState {
  IDLE,
  OFFER_RECEIVED,
  OFFER_ACCEPTED,
  OFFER_REJECTED,
  PAYMENT_PROCESSING,
  TRANSACTION_CONFIRMED,
  ERROR_DISPLAY
};

DisplayState currentState = IDLE;
String currentTxHash = "";
String currentAmount = "";
String currentProduct = "";
unsigned long stateStartTime = 0;

// Transaction history (last 5 transactions)
struct Transaction {
  String txHash;
  String amount;
  String timestamp;
  bool confirmed;
};

Transaction txHistory[5];
int txHistoryIndex = 0;
int txHistoryCount = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.begin(16, 2);
  
  // Initialize pins
  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(blueLED, OUTPUT);
  pinMode(ackButton, INPUT_PULLUP);
  
  // Initialize LEDs
  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, LOW);
  digitalWrite(blueLED, LOW);
  
  // Display startup message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Arduino B Ready");
  lcd.setCursor(0, 1);
  lcd.print("Seller Agent");
  
  Serial.println("=======================================");
  Serial.println("Arduino B - Transaction Display System");
  Serial.println("=======================================");
  Serial.println("Commands:");
  Serial.println("- OFFER:amount:product - Offer received");
  Serial.println("- ACCEPTED:tx_hash - Offer accepted");
  Serial.println("- REJECTED:reason - Offer rejected");
  Serial.println("- CONFIRMED:tx_hash - Transaction confirmed");
  Serial.println("- HISTORY - Show transaction history");
  Serial.println("- RESET - Reset display");
  Serial.println("=======================================");
  
  delay(3000);
  currentState = IDLE;
  updateDisplay();
}

void loop() {
  // Handle serial communication
  handleSerial();
  
  // Check button press for acknowledgment
  checkAckButton();
  
  // Update LEDs based on current state
  updateLEDs();
  
  // Auto-advance certain states after timeout
  handleStateTimeout();
  
  delay(100);
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
  Serial.println("Arduino B received: " + command);
  
  if (command.startsWith("OFFER:")) {
    // Parse: OFFER:150.5:Arduino Sensor Data
    int firstColon = command.indexOf(':');
    int secondColon = command.indexOf(':', firstColon + 1);
    
    currentAmount = command.substring(firstColon + 1, secondColon);
    currentProduct = command.substring(secondColon + 1);
    
    currentState = OFFER_RECEIVED;
    stateStartTime = millis();
    updateDisplay();
    
    Serial.println("Offer received: " + currentAmount + " ADA for " + currentProduct);
  }
  else if (command.startsWith("ACCEPTED:")) {
    // Parse: ACCEPTED:tx_hash_12345
    currentTxHash = command.substring(command.indexOf(':') + 1);
    
    currentState = OFFER_ACCEPTED;
    stateStartTime = millis();
    updateDisplay();
    
    Serial.println("Offer accepted! Transaction: " + currentTxHash);
  }
  else if (command.startsWith("REJECTED:")) {
    // Parse: REJECTED:Amount too low
    String reason = command.substring(command.indexOf(':') + 1);
    
    currentState = OFFER_REJECTED;
    stateStartTime = millis();
    updateDisplay();
    
    Serial.println("Offer rejected: " + reason);
  }
  else if (command.startsWith("PROCESSING:")) {
    // Parse: PROCESSING:tx_hash_12345
    currentTxHash = command.substring(command.indexOf(':') + 1);
    
    currentState = PAYMENT_PROCESSING;
    stateStartTime = millis();
    updateDisplay();
    
    Serial.println("Payment processing: " + currentTxHash);
  }
  else if (command.startsWith("CONFIRMED:") || command.indexOf(":CONFIRMED") > 0) {
    // Parse: CONFIRMED:tx_hash_12345 or tx_hash_12345:CONFIRMED
    String txHash;
    
    if (command.startsWith("CONFIRMED:")) {
      txHash = command.substring(command.indexOf(':') + 1);
    } else {
      txHash = command.substring(0, command.indexOf(':'));
    }
    
    currentTxHash = txHash;
    currentState = TRANSACTION_CONFIRMED;
    stateStartTime = millis();
    
    // Add to transaction history
    addToHistory(txHash, currentAmount, true);
    
    updateDisplay();
    
    Serial.println("🎉 TRANSACTION CONFIRMED: " + txHash);
    Serial.println("Amount: " + currentAmount + " ADA");
    Serial.println("Product: " + currentProduct);
  }
  else if (command == "HISTORY") {
    showTransactionHistory();
  }
  else if (command == "RESET") {
    resetSystem();
  }
  else if (command == "STATUS") {
    Serial.println("Current State: " + getStateName(currentState));
    Serial.println("TX Hash: " + currentTxHash);
    Serial.println("Amount: " + currentAmount);
    Serial.println("Product: " + currentProduct);
  }
  else {
    Serial.println("Unknown command: " + command);
  }
}

void updateDisplay() {
  lcd.clear();
  
  switch (currentState) {
    case IDLE:
      lcd.setCursor(0, 0);
      lcd.print("Agent B Ready");
      lcd.setCursor(0, 1);
      lcd.print("Waiting offers...");
      break;
      
    case OFFER_RECEIVED:
      lcd.setCursor(0, 0);
      lcd.print("Offer: " + currentAmount.substring(0, 5) + " ADA");
      lcd.setCursor(0, 1);
      lcd.print(currentProduct.substring(0, 16));
      break;
      
    case OFFER_ACCEPTED:
      lcd.setCursor(0, 0);
      lcd.print("✓ ACCEPTED");
      lcd.setCursor(0, 1);
      lcd.print("TX: " + currentTxHash.substring(0, 12));
      break;
      
    case OFFER_REJECTED:
      lcd.setCursor(0, 0);
      lcd.print("✗ REJECTED");
      lcd.setCursor(0, 1);
      lcd.print("Amount too low");
      break;
      
    case PAYMENT_PROCESSING:
      lcd.setCursor(0, 0);
      lcd.print("Processing...");
      lcd.setCursor(0, 1);
      lcd.print(currentTxHash.substring(0, 16));
      break;
      
    case TRANSACTION_CONFIRMED:
      lcd.setCursor(0, 0);
      lcd.print("✅ CONFIRMED");
      lcd.setCursor(0, 1);
      lcd.print(currentTxHash.substring(0, 16));
      break;
      
    case ERROR_DISPLAY:
      lcd.setCursor(0, 0);
      lcd.print("ERROR");
      lcd.setCursor(0, 1);
      lcd.print("Check connection");
      break;
  }
}

void updateLEDs() {
  // Reset all LEDs
  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, LOW);
  digitalWrite(blueLED, LOW);
  
  switch (currentState) {
    case IDLE:
      // Gentle blue pulse
      digitalWrite(blueLED, (millis() / 2000) % 2);
      break;
      
    case OFFER_RECEIVED:
      // Blue blink - processing
      digitalWrite(blueLED, (millis() / 500) % 2);
      break;
      
    case OFFER_ACCEPTED:
    case PAYMENT_PROCESSING:
      // Blue fast blink - payment processing
      digitalWrite(blueLED, (millis() / 200) % 2);
      break;
      
    case OFFER_REJECTED:
      // Red solid
      digitalWrite(redLED, HIGH);
      break;
      
    case TRANSACTION_CONFIRMED:
      // Green solid
      digitalWrite(greenLED, HIGH);
      break;
      
    case ERROR_DISPLAY:
      // Red blink
      digitalWrite(redLED, (millis() / 300) % 2);
      break;
  }
}

void checkAckButton() {
  int buttonState = digitalRead(ackButton);
  
  if (lastButtonState == HIGH && buttonState == LOW) {
    // Button pressed - acknowledge current state
    Serial.println("Button pressed - acknowledging current state");
    
    switch (currentState) {
      case OFFER_REJECTED:
      case TRANSACTION_CONFIRMED:
      case ERROR_DISPLAY:
        currentState = IDLE;
        currentTxHash = "";
        currentAmount = "";
        currentProduct = "";
        updateDisplay();
        break;
        
      default:
        // Button press in other states - show status
        Serial.println("Status: " + getStateName(currentState));
        break;
    }
  }
  
  lastButtonState = buttonState;
}

void handleStateTimeout() {
  unsigned long elapsed = millis() - stateStartTime;
  
  switch (currentState) {
    case OFFER_RECEIVED:
      if (elapsed > 10000) {  // 10 second timeout
        currentState = IDLE;
        updateDisplay();
      }
      break;
      
    case OFFER_REJECTED:
      if (elapsed > 5000) {   // 5 second timeout
        currentState = IDLE;
        updateDisplay();
      }
      break;
      
    case TRANSACTION_CONFIRMED:
      if (elapsed > 10000) {  // 10 second timeout
        currentState = IDLE;
        updateDisplay();
      }
      break;
      
    case ERROR_DISPLAY:
      if (elapsed > 5000) {   // 5 second timeout
        currentState = IDLE;
        updateDisplay();
      }
      break;
  }
}

void addToHistory(String txHash, String amount, bool confirmed) {
  txHistory[txHistoryIndex].txHash = txHash;
  txHistory[txHistoryIndex].amount = amount;
  txHistory[txHistoryIndex].timestamp = String(millis() / 1000);
  txHistory[txHistoryIndex].confirmed = confirmed;
  
  txHistoryIndex = (txHistoryIndex + 1) % 5;
  if (txHistoryCount < 5) txHistoryCount++;
  
  Serial.println("Added to history: " + txHash);
}

void showTransactionHistory() {
  Serial.println("===== Transaction History =====");
  
  if (txHistoryCount == 0) {
    Serial.println("No transactions recorded");
    return;
  }
  
  for (int i = 0; i < txHistoryCount; i++) {
    int index = (txHistoryIndex - 1 - i + 5) % 5;
    if (index < 0) index += 5;
    
    Serial.print(String(i + 1) + ". ");
    Serial.print("TX: " + txHistory[index].txHash.substring(0, 16) + "...");
    Serial.print(" | Amount: " + txHistory[index].amount + " ADA");
    Serial.print(" | Time: " + txHistory[index].timestamp + "s");
    Serial.println(" | Status: " + (txHistory[index].confirmed ? "CONFIRMED" : "PENDING"));
  }
  
  Serial.println("===============================");
}

void resetSystem() {
  currentState = IDLE;
  currentTxHash = "";
  currentAmount = "";
  currentProduct = "";
  stateStartTime = millis();
  
  // Clear history
  txHistoryCount = 0;
  txHistoryIndex = 0;
  
  Serial.println("Arduino B system reset");
  updateDisplay();
}

String getStateName(DisplayState state) {
  switch (state) {
    case IDLE: return "IDLE";
    case OFFER_RECEIVED: return "OFFER_RECEIVED";
    case OFFER_ACCEPTED: return "OFFER_ACCEPTED";
    case OFFER_REJECTED: return "OFFER_REJECTED";
    case PAYMENT_PROCESSING: return "PAYMENT_PROCESSING";
    case TRANSACTION_CONFIRMED: return "TRANSACTION_CONFIRMED";
    case ERROR_DISPLAY: return "ERROR_DISPLAY";
    default: return "UNKNOWN";
  }
}

// Test function for demonstration
void runDemoSequence() {
  Serial.println("Running demo sequence...");
  
  // Simulate offer received
  processSerialCommand("OFFER:150.5:Arduino Sensor Data");
  delay(3000);
  
  // Simulate offer accepted
  processSerialCommand("ACCEPTED:demo_tx_12345");
  delay(3000);
  
  // Simulate transaction confirmed
  processSerialCommand("CONFIRMED:demo_tx_12345");
  delay(5000);
  
  // Return to idle
  resetSystem();
  
  Serial.println("Demo sequence completed");
}