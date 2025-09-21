/*
 * Arduino B - Transaction Display
 * Displays transaction hash when payment is confirmed
 * Designed for Wokwi simulation with LCD and Serial Monitor
 */

#include <LiquidCrystal.h>

// LCD connections (adjust pins for your setup)
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// Serial communication
String incomingData = "";
bool dataComplete = false;

// Display states
enum DisplayState {
  WAITING,
  CONFIRMED,
  ERROR
};

DisplayState currentState = WAITING;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.begin(16, 2);
  
  // Display startup message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Agent B Ready");
  lcd.setCursor(0, 1);
  lcd.print("Waiting...");
  
  Serial.println("Arduino B - Transaction Display Started");
  Serial.println("Waiting for transaction confirmations...");
  Serial.println("Format: tx_hash:CONFIRMED");
  Serial.println("Example: mock_tx_1234567890_150.50:CONFIRMED");
  Serial.println("----------------------------------------");
}

void loop() {
  // Check for incoming serial data
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      dataComplete = true;
    } else {
      incomingData += inChar;
    }
  }
  
  // Process complete data
  if (dataComplete) {
    processIncomingData();
    incomingData = "";
    dataComplete = false;
  }
  
  // Update display based on current state
  updateDisplay();
  
  delay(100);
}

void processIncomingData() {
  Serial.print("Received: ");
  Serial.println(incomingData);
  
  // Parse the incoming data
  // Expected format: "tx_hash:CONFIRMED" or "tx_hash:ERROR"
  int colonIndex = incomingData.indexOf(':');
  
  if (colonIndex > 0) {
    String txHash = incomingData.substring(0, colonIndex);
    String status = incomingData.substring(colonIndex + 1);
    
    Serial.print("Transaction Hash: ");
    Serial.println(txHash);
    Serial.print("Status: ");
    Serial.println(status);
    
    if (status == "CONFIRMED") {
      displayConfirmedTransaction(txHash);
      currentState = CONFIRMED;
    } else if (status == "ERROR") {
      displayError(status);
      currentState = ERROR;
    } else {
      Serial.println("Unknown status received");
    }
  } else {
    // Try to parse as just transaction hash
    if (incomingData.length() > 0) {
      displayConfirmedTransaction(incomingData);
      currentState = CONFIRMED;
    }
  }
}

void displayConfirmedTransaction(String txHash) {
  Serial.println("========================================");
  Serial.println("✅ CONFIRMED TRANSACTION");
  Serial.print("Hash: ");
  Serial.println(txHash);
  Serial.println("========================================");
  
  // Update LCD display
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("✅ CONFIRMED");
  lcd.setCursor(0, 1);
  
  // Display first 16 characters of tx_hash
  String displayHash = txHash;
  if (displayHash.length() > 16) {
    displayHash = displayHash.substring(0, 16);
  }
  lcd.print(displayHash);
  
  // Blink the display for attention
  for (int i = 0; i < 3; i++) {
    lcd.noDisplay();
    delay(200);
    lcd.display();
    delay(200);
  }
}

void displayError(String errorMsg) {
  Serial.println("========================================");
  Serial.println("❌ ERROR");
  Serial.print("Message: ");
  Serial.println(errorMsg);
  Serial.println("========================================");
  
  // Update LCD display
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("❌ ERROR");
  lcd.setCursor(0, 1);
  lcd.print("Check Serial");
  
  currentState = ERROR;
}

void updateDisplay() {
  static unsigned long lastUpdate = 0;
  static bool displayOn = true;
  
  // Update display every 2 seconds
  if (millis() - lastUpdate > 2000) {
    lastUpdate = millis();
    
    switch (currentState) {
      case WAITING:
        // Blink "Waiting..." message
        if (displayOn) {
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Agent B Ready");
          lcd.setCursor(0, 1);
          lcd.print("Waiting...");
        } else {
          lcd.clear();
        }
        displayOn = !displayOn;
        break;
        
      case CONFIRMED:
        // Keep confirmed message visible
        break;
        
      case ERROR:
        // Blink error message
        if (displayOn) {
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("❌ ERROR");
          lcd.setCursor(0, 1);
          lcd.print("Check Serial");
        } else {
          lcd.clear();
        }
        displayOn = !displayOn;
        break;
    }
  }
}

// Function to reset display to waiting state
void resetToWaiting() {
  currentState = WAITING;
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Agent B Ready");
  lcd.setCursor(0, 1);
  lcd.print("Waiting...");
  Serial.println("Reset to waiting state");
}

// Function to test display with mock data
void testDisplay() {
  Serial.println("Testing display with mock transaction...");
  displayConfirmedTransaction("mock_tx_test_1234567890");
  delay(3000);
  resetToWaiting();
}
