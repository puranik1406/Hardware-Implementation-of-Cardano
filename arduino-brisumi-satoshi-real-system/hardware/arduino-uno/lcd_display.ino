/*
 * Arduino Uno #2 - LCD Transaction Display (COM3)
 * Hardware: 16x2 I2C LCD (SDA=A4, SCL=A5)
 * Purpose: Display transaction hash and status from PC
 * 
 * LCD I2C Address: 0x27 (common) or 0x3F (try if 0x27 doesn't work)
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize LCD - try 0x27 first, if not working try 0x3F
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  // Start serial communication
  Serial.begin(9600);
  
  // Initialize I2C LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // Display startup message
  lcd.setCursor(0, 0);
  lcd.print("Cardano Display");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  Serial.println("READY");
  Serial.println("Arduino LCD Display initialized on COM3");
  
  delay(2000);
  
  // Ready state
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Ready for TX");
  lcd.setCursor(0, 1);
  lcd.print("Waiting...");
}

void loop() {
  // Listen for commands from PC
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  
  delay(100);
}

void processCommand(String command) {
  if (command.startsWith("TX:")) {
    // Display transaction hash
    String txHash = command.substring(3);
    displayTransaction(txHash);
  }
  else if (command.startsWith("STATUS:")) {
    // Display status message
    String status = command.substring(7);
    displayStatus(status);
  }
  else if (command.startsWith("ERROR:")) {
    // Display error
    String error = command.substring(6);
    displayError(error);
  }
  else if (command.startsWith("REASON:")) {
    // Display rejection reason
    String reason = command.substring(7);
    displayReason(reason);
  }
  else if (command == "CLEAR") {
    // Clear display
    clearDisplay();
  }
  else if (command == "REQUEST_LATEST_TX") {
    // Send acknowledgment
    Serial.println("ACK");
  }
}

void displayTransaction(const String &txHash) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TX Success!");
  lcd.setCursor(0, 1);
  
  // Display truncated hash (16 chars max)
  if (txHash.length() <= 16) {
    lcd.print(txHash);
  } else {
    // Show first 13 chars + "..."
    lcd.print(txHash.substring(0, 13) + "...");
  }
  
  // Flash backlight to indicate new transaction
  for(int i = 0; i < 2; i++) {
    lcd.noBacklight();
    delay(200);
    lcd.backlight();
    delay(200);
  }
  
  Serial.println("Displayed: " + txHash);
}

void displayStatus(const String &status) {
  lcd.clear();
  lcd.setCursor(0, 0);
  
  if (status == "Transaction sent") {
    lcd.print("Sending TX...");
  } else if (status == "REJECTED") {
    lcd.print("TX REJECTED!");
    lcd.setCursor(0, 1);
    lcd.print("Emotion Check");
    
    // Flash backlight for rejection
    for(int i = 0; i < 3; i++) {
      lcd.noBacklight();
      delay(300);
      lcd.backlight();
      delay(300);
    }
  } else {
    lcd.print("Status:");
    lcd.setCursor(0, 1);
    if (status.length() <= 16) {
      lcd.print(status);
    } else {
      lcd.print(status.substring(0, 16));
    }
  }
  
  Serial.println("Status: " + status);
}

void displayError(const String &error) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ERROR!");
  lcd.setCursor(0, 1);
  
  if (error.length() <= 16) {
    lcd.print(error);
  } else {
    lcd.print(error.substring(0, 16));
  }
  
  // Flash backlight rapidly for error
  for(int i = 0; i < 5; i++) {
    lcd.noBacklight();
    delay(150);
    lcd.backlight();
    delay(150);
  }
  
  Serial.println("Error: " + error);
}

void displayReason(const String &reason) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Reason:");
  lcd.setCursor(0, 1);
  
  if (reason.length() <= 16) {
    lcd.print(reason);
  } else {
    // Scroll long reasons
    lcd.print(reason.substring(0, 16));
    delay(2000);
    
    // Scroll if longer
    if (reason.length() > 16) {
      for(int i = 0; i < reason.length() - 16; i++) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Reason:");
        lcd.setCursor(0, 1);
        lcd.print(reason.substring(i, i + 16));
        delay(300);
      }
    }
  }
  
  Serial.println("Reason: " + reason);
}

void clearDisplay() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Ready for TX");
  lcd.setCursor(0, 1);
  lcd.print("Waiting...");
  
  Serial.println("Display cleared");
}
