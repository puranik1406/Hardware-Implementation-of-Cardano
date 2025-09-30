// Arduino Uno – Transaction Display
// I2C LCD 16x2 on A4 (SDA) A5 (SCL)
// Ethernet shield or USB communication for transaction polling

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// LCD Configuration
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Transaction polling configuration
unsigned long lastPollTime = 0;
const unsigned long POLL_INTERVAL = 3000; // Poll every 3 seconds
String lastTxHash = "";

void setup() {
  Serial.begin(9600);
  
  // Initialize I2C LCD (Arduino Uno: SDA=A4, SCL=A5)
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // Display startup message
  lcd.setCursor(0, 0);
  lcd.print("Cardano Display");
  lcd.setCursor(0, 1);
  lcd.print("Waiting for TX...");
  
  Serial.println("Arduino Transaction Display Ready");
  Serial.println("Waiting for transaction data...");
  
  delay(2000);
}

void loop() {
  // Check for incoming serial data (transaction hash from PC/Arduino Bridge)
  if (Serial.available()) {
    String incomingData = Serial.readStringUntil('\n');
    incomingData.trim();
    
    if (incomingData.startsWith("TX:")) {
      String txHash = incomingData.substring(3); // Remove "TX:" prefix
      displayTransaction(txHash);
      lastTxHash = txHash;
    }
    else if (incomingData.startsWith("STATUS:")) {
      String status = incomingData.substring(7); // Remove "STATUS:" prefix
      displayStatus(status);
    }
    else if (incomingData.startsWith("ERROR:")) {
      String error = incomingData.substring(6); // Remove "ERROR:" prefix
      displayError(error);
    }
    else if (incomingData == "CLEAR") {
      clearDisplay();
    }
  }
  
  // Periodic polling mode (if no direct communication)
  if (millis() - lastPollTime > POLL_INTERVAL) {
    lastPollTime = millis();
    requestLatestTransaction();
  }
  
  delay(100);
}

void displayTransaction(const String &txHash) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("New Transaction:");
  lcd.setCursor(0, 1);
  
  if (txHash.length() <= 16) {
    lcd.print(txHash);
  } else {
    // Display first 13 chars + "..."
    lcd.print(txHash.substring(0, 13) + "...");
  }
  
  Serial.println("Displayed TX: " + txHash);
}

void displayStatus(const String &status) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Status:");
  lcd.setCursor(0, 1);
  
  if (status.length() <= 16) {
    lcd.print(status);
  } else {
    lcd.print(status.substring(0, 16));
  }
  
  Serial.println("Status: " + status);
}

void displayError(const String &error) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ERROR:");
  lcd.setCursor(0, 1);
  
  if (error.length() <= 16) {
    lcd.print(error);
  } else {
    lcd.print(error.substring(0, 16));
  }
  
  Serial.println("Error: " + error);
  
  // Flash display for error indication
  for (int i = 0; i < 3; i++) {
    lcd.noBacklight();
    delay(200);
    lcd.backlight();
    delay(200);
  }
}

void clearDisplay() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Cardano Display");
  lcd.setCursor(0, 1);
  lcd.print("Ready...");
  
  Serial.println("Display cleared");
}

void requestLatestTransaction() {
  // Send request to PC/Arduino Bridge for latest transaction
  Serial.println("REQUEST_LATEST_TX");
}

// Optional: Display connection status
void displayConnectionStatus(bool connected) {
  if (!connected) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Connection Lost");
    lcd.setCursor(0, 1);
    lcd.print("Reconnecting...");
  }
}

// Optional: Display wallet balance
void displayBalance(const String &balance) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Balance:");
  lcd.setCursor(0, 1);
  lcd.print(balance + " ADA");
}