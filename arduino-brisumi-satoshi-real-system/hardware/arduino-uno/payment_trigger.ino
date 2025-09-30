// Arduino Uno – Payment Trigger with LCD Display
// Button on pin 2, LEDs on pins 11-13
// I2C LCD 16x2 on A4 (SDA) A5 (SCL)

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const int BUTTON_PIN = 2;
const int LED_OK = 13;
const int LED_BUSY = 12;
const int LED_ERR = 11;

volatile bool buttonPressed = false;
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_OK, OUTPUT);
  pinMode(LED_BUSY, OUTPUT);
  pinMode(LED_ERR, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), onButton, FALLING);
  Serial.begin(9600);
  
  // Initialize LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Cardano Ready");
  lcd.setCursor(0, 1);
  lcd.print("Press Button");
  
  digitalWrite(LED_OK, LOW);
  digitalWrite(LED_BUSY, LOW);
  digitalWrite(LED_ERR, LOW);
}

void onButton() {
  buttonPressed = true;
}

void loop() {
  if (buttonPressed) {
    buttonPressed = false;
    digitalWrite(LED_BUSY, HIGH);
    
    // Update LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sending Payment");
    lcd.setCursor(0, 1);
    lcd.print("Please wait...");
    
    delay(50);
    Serial.println("TRIGGER_PAYMENT");
    Serial.println("FROM_AGENT:satoshi_alpha_001");
    Serial.println("TO_AGENT:satoshi_beta_002");
    Serial.println("AMOUNT:2.5");
    Serial.println("END_COMMAND");
    
    // Wait for response line like TX:...
    unsigned long start = millis();
    bool txReceived = false;
    String txHash = "";
    
    while (millis() - start < 10000) { // Wait up to 10 seconds
      if (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        if (line.startsWith("TX:")) {
          txHash = line.substring(3); // Remove "TX:" prefix
          txReceived = true;
          digitalWrite(LED_OK, HIGH);
          break;
        } else if (line.startsWith("ERROR:")) {
          digitalWrite(LED_ERR, HIGH);
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Transaction");
          lcd.setCursor(0, 1);
          lcd.print("Failed!");
          delay(3000);
          digitalWrite(LED_ERR, LOW);
          break;
        }
      }
    }
    
    if (txReceived) {
      // Display transaction hash
      displayTxHash(txHash);
      delay(500);
      digitalWrite(LED_OK, LOW);
    } else {
      // Timeout - no response
      digitalWrite(LED_ERR, HIGH);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("No Response");
      lcd.setCursor(0, 1);
      lcd.print("Try Again");
      delay(3000);
      digitalWrite(LED_ERR, LOW);
    }
    
    digitalWrite(LED_BUSY, LOW);
    
    // Return to ready state after 5 seconds
    delay(5000);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Cardano Ready");
    lcd.setCursor(0, 1);
    lcd.print("Press Button");
  }
}

void displayTxHash(const String &txHash) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TX Hash:");
  lcd.setCursor(0, 1);
  
  if (txHash.length() <= 16) {
    lcd.print(txHash);
  } else {
    // Display first 16 characters, then scroll through
    lcd.print(txHash.substring(0, 16));
    delay(2000);
    
    // If hash is longer, scroll through it
    if (txHash.length() > 16) {
      for (int i = 1; i <= txHash.length() - 16; i++) {
        lcd.setCursor(0, 1);
        lcd.print(txHash.substring(i, i + 16));
        delay(300);
      }
    }
  }
}
