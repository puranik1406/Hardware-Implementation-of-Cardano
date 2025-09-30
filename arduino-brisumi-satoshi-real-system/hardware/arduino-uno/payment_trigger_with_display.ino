// Arduino Uno – Payment Trigger with LCD Display
// Button on pin 2, LEDs on pins 11-13
// I2C LCD 16x2 on A4 (SDA) A5 (SCL)
// 
// Hardware Setup:
// - Button: Pin 2 (with pullup resistor)
// - LED OK: Pin 13 (Green)
// - LED BUSY: Pin 12 (Yellow) 
// - LED ERR: Pin 11 (Red)
// - LCD: A4 (SDA), A5 (SCL) - I2C Address 0x27
//
// Install Library: LiquidCrystal I2C by Frank de Brabander

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Pin definitions
const int BUTTON_PIN = 2;
const int LED_OK = 13;
const int LED_BUSY = 12;
const int LED_ERR = 11;

// LCD setup (I2C address 0x27, 16 columns, 2 rows)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// State variables
volatile bool buttonPressed = false;
String lastTxHash = "";
unsigned long lastDisplayUpdate = 0;
bool waitingForTx = false;

void setup() {
  // Initialize pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_OK, OUTPUT);
  pinMode(LED_BUSY, OUTPUT);
  pinMode(LED_ERR, OUTPUT);
  
  // Attach button interrupt
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), onButton, FALLING);
  
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // Initial display
  displayStatus("Cardano Payment", "System Ready");
  
  // Turn off all LEDs
  digitalWrite(LED_OK, LOW);
  digitalWrite(LED_BUSY, LOW);
  digitalWrite(LED_ERR, LOW);
  
  delay(2000);
  displayStatus("Press Button", "for Payment");
}

void onButton() {
  buttonPressed = true;
}

void loop() {
  // Handle button press
  if (buttonPressed) {
    buttonPressed = false;
    triggerPayment();
  }
  
  // Check for incoming serial data (transaction responses)
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    handleSerialResponse(line);
  }
  
  // Update display periodically
  if (millis() - lastDisplayUpdate > 1000) {
    updateDisplay();
    lastDisplayUpdate = millis();
  }
  
  // Timeout for waiting transactions
  if (waitingForTx && millis() - lastDisplayUpdate > 10000) {
    displayStatus("Timeout", "Try Again");
    digitalWrite(LED_BUSY, LOW);
    digitalWrite(LED_ERR, HIGH);
    delay(1000);
    digitalWrite(LED_ERR, LOW);
    waitingForTx = false;
  }
}

void triggerPayment() {
  // Visual feedback
  digitalWrite(LED_BUSY, HIGH);
  displayStatus("Sending...", "Payment Request");
  
  // Send payment command via serial
  Serial.println("TRIGGER_PAYMENT");
  Serial.println("FROM_AGENT:satoshi_alpha_001");
  Serial.println("TO_AGENT:satoshi_beta_002");
  Serial.println("AMOUNT:2.5");
  Serial.println("END_COMMAND");
  
  waitingForTx = true;
  lastDisplayUpdate = millis();
}

void handleSerialResponse(String line) {
  if (line.startsWith("TX:")) {
    // Extract transaction hash
    String txHash = line.substring(3);
    txHash.trim();
    
    if (txHash.length() > 0 && !txHash.equals("ERR")) {
      // Successful transaction
      lastTxHash = txHash;
      displayTransaction(txHash);
      digitalWrite(LED_BUSY, LOW);
      digitalWrite(LED_OK, HIGH);
      delay(2000);
      digitalWrite(LED_OK, LOW);
      waitingForTx = false;
    } else {
      // Transaction error
      displayStatus("TX Failed", "Check Wallet");
      digitalWrite(LED_BUSY, LOW);
      digitalWrite(LED_ERR, HIGH);
      delay(2000);
      digitalWrite(LED_ERR, LOW);
      waitingForTx = false;
    }
  } else if (line.startsWith("ERROR:")) {
    // Handle error messages
    String error = line.substring(6);
    displayStatus("Error:", error.substring(0, 14));
    digitalWrite(LED_BUSY, LOW);
    digitalWrite(LED_ERR, HIGH);
    delay(3000);
    digitalWrite(LED_ERR, LOW);
    waitingForTx = false;
  } else if (line.startsWith("STATUS:")) {
    // Handle status updates
    String status = line.substring(7);
    displayStatus("Status:", status.substring(0, 14));
  }
}

void displayStatus(String line1, String line2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1.substring(0, 16));
  lcd.setCursor(0, 1);
  lcd.print(line2.substring(0, 16));
}

void displayTransaction(String txHash) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TX Success!");
  lcd.setCursor(0, 1);
  
  // Display first 16 characters of transaction hash
  if (txHash.length() <= 16) {
    lcd.print(txHash);
  } else {
    // For long hashes, show first 14 chars + ".."
    lcd.print(txHash.substring(0, 14));
    lcd.print("..");
  }
}

void updateDisplay() {
  if (!waitingForTx && lastTxHash.length() == 0) {
    // Default display when idle
    displayStatus("Press Button", "for Payment");
  }
}

void displayScrollingHash(String txHash) {
  // Optional: implement scrolling for very long transaction hashes
  static int scrollPos = 0;
  static unsigned long lastScroll = 0;
  
  if (millis() - lastScroll > 500) {
    lcd.setCursor(0, 1);
    if (txHash.length() <= 16) {
      lcd.print(txHash);
    } else {
      String display = txHash.substring(scrollPos);
      if (display.length() < 16) {
        display += " " + txHash.substring(0, 16 - display.length());
      }
      lcd.print(display.substring(0, 16));
      scrollPos = (scrollPos + 1) % txHash.length();
    }
    lastScroll = millis();
  }
}