// ESP8266 NodeMCU – Transaction Display
// I2C LCD 16x2 on D1 (SCL) D2 (SDA)
// WiFi credentials via constants or serial config

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// UPDATE: set these before flashing
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD"; 
const char* PC_HOST = "192.168.0.100"; // Your PC LAN IP running Masumi Payment service
String API_URL = String("http://") + PC_HOST + ":3001/api/latest-transaction";

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(115200);
  // Initialize I2C on ESP8266 pins (SDA=D2, SCL=D1)
  Wire.begin(D2, D1);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0,0); lcd.print("Connecting WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 60) {
    delay(500);
    lcd.setCursor(0,1); lcd.print("...");
    tries++;
  }
  lcd.clear();
  if (WiFi.status() == WL_CONNECTED) {
    lcd.setCursor(0,0); lcd.print("WiFi OK");
  } else {
    lcd.setCursor(0,0); lcd.print("WiFi FAIL");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, API_URL.c_str());
    int httpCode = http.GET();
    if (httpCode == 200) {
      String response = http.getString();
      String txHash = parseTxHash(response);
      displayTx(txHash);
    } else {
      displayTx("HTTP:" + String(httpCode));
    }
    http.end();
  } else {
    lcd.clear();
    lcd.setCursor(0,0); lcd.print("WiFi Reconnect");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASS);
  }
  delay(3000);
}

String parseTxHash(const String &json) {
  int idx = json.indexOf("\"tx_id\":");
  if (idx < 0) return "No tx";
  int start = json.indexOf('"', idx + 8);
  int end = json.indexOf('"', start + 1);
  if (start < 0 || end < 0) return "No tx";
  return json.substring(start + 1, end);
}

void displayTx(const String &tx) {
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("TX Hash:");
  lcd.setCursor(0,1);
  if (tx.length() <= 16) {
    lcd.print(tx);
  } else {
    lcd.print(tx.substring(0,16));
  }
}
