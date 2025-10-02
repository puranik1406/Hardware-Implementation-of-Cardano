#include <Wire.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>  // auto-detect PCF8574 mapping

hd44780_I2Cexp lcd;

unsigned long lastPoll = 0;
const unsigned long POLL_MS = 3000;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  Serial.setTimeout(50);
  delay(100);

  Wire.begin();              // UNO: SDA=A4, SCL=A5
  Wire.setClock(100000);

  int status = lcd.begin(16, 2);  // non-zero on error
  if (status) {
    Serial.print("LCD_ERROR: begin()="); Serial.println(status);
    // Blink LED to indicate init failure
    for (;;) { digitalWrite(LED_BUILTIN, HIGH); delay(250);
               digitalWrite(LED_BUILTIN, LOW);  delay(250); }
  }

  // Initial screen (same reliable init flow as your working sketch)
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("Cardano Display");
  lcd.setCursor(0, 1); lcd.print("Waiting for TX...");
  Serial.println("[LCD] READY");
  // Handshake with Arduino Bridge
  Serial.println("HELLO_DISPLAY");
  Serial.println("REQUEST_LATEST_TX");
}

void loop() {
  // Read newline-terminated messages from the bridge
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length()) {
      Serial.print("[LCD] RX: "); Serial.println(line);
      handleLine(line);
    }
  }

  // Periodic re-sync (bridge should answer with last TX/status)
  if (millis() - lastPoll >= POLL_MS) {
    lastPoll = millis();
    Serial.println("REQUEST_LATEST_TX");
  }

  // Heartbeat indicator
  static unsigned long t=0; static bool on=false;
  if (millis()-t > 600) {
    t = millis(); on = !on;
    lcd.setCursor(15, 1); lcd.print(on ? "*" : " ");
  }
}

void handleLine(const String& line) {
  if (line.startsWith("TX:")) {
    showTx(line.substring(3));
  } else if (line.startsWith("STATUS:")) {
    showStatus(line.substring(7));
  } else if (line.startsWith("ERROR:")) {
    showError(line.substring(6));
  } else if (line == "CLEAR") {
    showReady();
  } else if (line == "TEST") {
    lcd.clear();
    lcd.setCursor(0,0); lcd.print("HELLO CARDANO!");
    lcd.setCursor(0,1); lcd.print("I2C LCD (auto)");
  }
}

void showTx(const String& hash) {
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("TX Confirmed!");
  // If hash fits, show directly; else scroll it so full hash is visible
  if (hash.length() <= 16) {
    lcd.setCursor(0, 1); lcd.print(hash);
  } else {
    // Non-fancy marquee for reliability
    for (int i = 0; i <= hash.length() - 16; i++) {
      lcd.setCursor(0, 1);
      lcd.print(hash.substring(i, i + 16));
      delay(200);
    }
    // Leave first 13 chars + ... at the end
    lcd.setCursor(0, 1);
    lcd.print(hash.substring(0, 13)); lcd.print("...");
  }
  Serial.print("[LCD] Displayed TX: ");
  Serial.println(hash);
}

void showStatus(const String& s) {
  lcd.clear();
  lcd.setCursor(0,0); lcd.print("Status:");
  lcd.setCursor(0,1); lcd.print(s.substring(0,16));
  Serial.print("[LCD] STATUS: "); Serial.println(s);
}

void showError(const String& e) {
  lcd.clear();
  lcd.setCursor(0,0); lcd.print("ERROR:");
  lcd.setCursor(0,1); lcd.print(e.substring(0,16));
  Serial.print("[LCD] ERROR: "); Serial.println(e);
}

void showReady() {
  lcd.clear();
  lcd.setCursor(0,0); lcd.print("Cardano Display");
  lcd.setCursor(0,1); lcd.print("Ready...");
  Serial.println("[LCD] READY screen");
}