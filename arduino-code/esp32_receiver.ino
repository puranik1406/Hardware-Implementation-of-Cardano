// ESP32 Code for Transaction Hash Display
// Receives transaction hashes wirelessly and displays them

#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>  // For LCD display (optional)

// WiFi credentials
const char* ssid = "YourWiFi";           // Replace with your WiFi name
const char* password = "YourPassword";    // Replace with your WiFi password

// Pin definitions
const int LED_SUCCESS = 2;      // Green LED for successful transactions
const int LED_ERROR = 4;        // Red LED for failed transactions
const int BUZZER_PIN = 5;       // Buzzer for notifications
const int DISPLAY_PIN = 18;     // Pin for additional display

// LCD Display (optional - comment out if not using)
// LiquidCrystal_I2C lcd(0x27, 16, 2);  // I2C address, columns, rows

// WebSocket server
WebSocketsServer webSocket = WebSocketsServer(81);

// Agent configuration
String agentId = "esp32_receiver_001";
String agentName = "ESP32 Display";
bool wifiConnected = false;

// Transaction display variables
struct Transaction {
  String txHash;
  float amount;
  String status;
  unsigned long timestamp;
  bool displayed;
};

Transaction currentTx = {"", 0, "", 0, false};
Transaction lastTxHistory[10];  // Store last 10 transactions
int txHistoryCount = 0;

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(LED_SUCCESS, OUTPUT);
  pinMode(LED_ERROR, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(DISPLAY_PIN, OUTPUT);
  
  // Initialize LCD (uncomment if using)
  // lcd.init();
  // lcd.backlight();
  // lcd.setCursor(0, 0);
  // lcd.print("ESP32 Masumi");
  // lcd.setCursor(0, 1);
  // lcd.print("Initializing...");
  
  Serial.println("=== ESP32 Masumi Transaction Display ===");
  Serial.println("Agent ID: " + agentId);
  Serial.println("Agent Name: " + agentName);
  
  // Connect to WiFi
  connectToWiFi();
  
  if (wifiConnected) {
    // Start WebSocket server
    webSocket.begin();
    webSocket.onEvent(webSocketEvent);
    
    Serial.println("WebSocket server started on port 81");
    Serial.println("Ready to receive transaction hashes!");
    
    // Update LCD
    // lcd.clear();
    // lcd.setCursor(0, 0);
    // lcd.print("WiFi Connected");
    // lcd.setCursor(0, 1);
    // lcd.print(WiFi.localIP());
    
    playConnectedTone();
  } else {
    Serial.println("ERROR: WiFi connection failed!");
    playErrorTone();
  }
  
  Serial.println("Commands: DISPLAY_TX:<hash>:<amount>:<status>");
  Serial.println("          GET_STATUS");
  Serial.println("          SHOW_HISTORY");
  Serial.println("=========================================");
}

void loop() {
  // Handle WebSocket events
  if (wifiConnected) {
    webSocket.loop();
  }
  
  // Check for serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processSerialCommand(command);
  }
  
  // Update display if new transaction
  if (!currentTx.displayed && currentTx.txHash != "") {
    displayTransaction(currentTx);
    currentTx.displayed = true;
  }
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED && wifiConnected) {
    wifiConnected = false;
    Serial.println("WiFi disconnected! Attempting reconnect...");
    connectToWiFi();
  }
  
  delay(100);
}

void connectToWiFi() {
  Serial.println("Connecting to WiFi: " + String(ssid));
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println();
    Serial.println("WiFi connected successfully!");
    Serial.println("IP address: " + WiFi.localIP().toString());
    Serial.println("WebSocket URL: ws://" + WiFi.localIP().toString() + ":81/");
    
    digitalWrite(LED_SUCCESS, HIGH);
    delay(1000);
    digitalWrite(LED_SUCCESS, LOW);
  } else {
    wifiConnected = false;
    Serial.println();
    Serial.println("WiFi connection failed!");
    
    digitalWrite(LED_ERROR, HIGH);
    delay(1000);
    digitalWrite(LED_ERROR, LOW);
  }
}

void processSerialCommand(String command) {
  Serial.println("Received: " + command);
  
  if (command.startsWith("DISPLAY_TX:")) {
    processDisplayTransaction(command);
  }
  else if (command == "GET_STATUS") {
    sendStatus();
  }
  else if (command == "SHOW_HISTORY") {
    showTransactionHistory();
  }
  else if (command.startsWith("SET_WIFI:")) {
    setWiFiCredentials(command);
  }
  else {
    Serial.println("ERROR: Unknown command - " + command);
  }
}

void processDisplayTransaction(String command) {
  // Parse: DISPLAY_TX:<hash>:<amount>:<status>
  int firstColon = command.indexOf(':', 11);
  int secondColon = command.indexOf(':', firstColon + 1);
  int thirdColon = command.indexOf(':', secondColon + 1);
  
  if (firstColon == -1 || secondColon == -1 || thirdColon == -1) {
    Serial.println("ERROR: Invalid display command format");
    return;
  }
  
  String txHash = command.substring(11, firstColon);
  float amount = command.substring(firstColon + 1, secondColon).toFloat();
  String status = command.substring(secondColon + 1, thirdColon);
  
  // Create new transaction
  Transaction newTx = {
    txHash,
    amount,
    status,
    millis(),
    false
  };
  
  currentTx = newTx;
  
  // Add to history
  if (txHistoryCount < 10) {
    lastTxHistory[txHistoryCount] = newTx;
    txHistoryCount++;
  } else {
    // Shift array and add new transaction
    for (int i = 0; i < 9; i++) {
      lastTxHistory[i] = lastTxHistory[i + 1];
    }
    lastTxHistory[9] = newTx;
  }
  
  Serial.println("New transaction received:");
  Serial.println("  Hash: " + txHash);
  Serial.println("  Amount: " + String(amount) + " ADA");
  Serial.println("  Status: " + status);
  
  // Send confirmation
  Serial.println("TX_RECEIVED:" + txHash + ":" + status);
  Serial.println("COMPLETE");
}

void displayTransaction(Transaction tx) {
  // Check if this is an AI-initiated transaction
  bool isAITransaction = tx.status.indexOf("AI") != -1;
  
  if (isAITransaction) {
    Serial.println("🤖 === AI AGENT TRANSACTION === 🤖");
    Serial.println("Initiated by: SATOSHI AI AGENT");
    Serial.println("Decision Type: AUTONOMOUS");
  } else {
    Serial.println("=== DISPLAYING TRANSACTION ===");
  }
  
  Serial.println("Hash: " + tx.txHash);
  Serial.println("Amount: " + String(tx.amount) + " ADA");
  Serial.println("Status: " + tx.status);
  Serial.println("Cardano Explorer: https://preprod.cardanoscan.io/transaction/" + tx.txHash);
  
  if (isAITransaction) {
    Serial.println("🧠 AI Analysis Complete");
    Serial.println("🎯 Autonomous Decision Executed");
  }
  
  Serial.println("==============================");
  
  // Update LCD display (uncomment if using)
  // lcd.clear();
  // if (isAITransaction) {
  //   lcd.setCursor(0, 0);
  //   lcd.print("AI: " + String(tx.amount) + " ADA");
  // } else {
  //   lcd.setCursor(0, 0);
  //   lcd.print("TX: " + String(tx.amount) + " ADA");
  // }
  // lcd.setCursor(0, 1);
  // lcd.print(tx.txHash.substring(0, 16));
  
  // Visual and audio feedback based on transaction type
  if (tx.status == "SUCCESS" || tx.status == "AI_SUCCESS") {
    if (isAITransaction) {
      // Special AI success pattern
      playAISuccessTone();
      
      // AI success pattern - alternating LEDs
      for (int i = 0; i < 4; i++) {
        digitalWrite(LED_SUCCESS, HIGH);
        delay(150);
        digitalWrite(LED_SUCCESS, LOW);
        delay(50);
        digitalWrite(LED_ERROR, HIGH);  // Use as second indicator
        delay(150);
        digitalWrite(LED_ERROR, LOW);
        delay(50);
      }
    } else {
      // Regular success indication
      digitalWrite(LED_SUCCESS, HIGH);
      playSuccessTone();
      delay(500);
      digitalWrite(LED_SUCCESS, LOW);
      
      // Flash success pattern
      for (int i = 0; i < 3; i++) {
        digitalWrite(LED_SUCCESS, HIGH);
        delay(200);
        digitalWrite(LED_SUCCESS, LOW);
        delay(200);
      }
    }
  } else {
    // Error indication
    digitalWrite(LED_ERROR, HIGH);
    playErrorTone();
    delay(500);
    digitalWrite(LED_ERROR, LOW);
    
    // Flash error pattern
    for (int i = 0; i < 5; i++) {
      digitalWrite(LED_ERROR, HIGH);
      delay(100);
      digitalWrite(LED_ERROR, LOW);
      delay(100);
    }
  }
  
  // Send transaction data via WebSocket
  if (wifiConnected) {
    StaticJsonDocument<500> txData;
    txData["type"] = isAITransaction ? "ai_transaction" : "transaction";
    txData["txHash"] = tx.txHash;
    txData["amount"] = tx.amount;
    txData["status"] = tx.status;
    txData["timestamp"] = tx.timestamp;
    txData["explorerUrl"] = "https://preprod.cardanoscan.io/transaction/" + tx.txHash;
    txData["aiInitiated"] = isAITransaction;
    txData["autonomous"] = isAITransaction;
    
    String txDataStr;
    serializeJson(txData, txDataStr);
    webSocket.broadcastTXT(txDataStr);
  }
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("WebSocket client disconnected: " + String(num));
      break;
      
    case WStype_CONNECTED:
      {
        IPAddress ip = webSocket.remoteIP(num);
        Serial.println("WebSocket client connected: " + ip.toString());
        
        // Send welcome message
        StaticJsonDocument<200> welcome;
        welcome["type"] = "welcome";
        welcome["agent_id"] = agentId;
        welcome["agent_name"] = agentName;
        welcome["message"] = "Connected to ESP32 transaction display";
        
        String welcomeStr;
        serializeJson(welcome, welcomeStr);
        webSocket.sendTXT(num, welcomeStr);
      }
      break;
      
    case WStype_TEXT:
      Serial.println("WebSocket message: " + String((char*)payload));
      break;
      
    default:
      break;
  }
}

void sendStatus() {
  StaticJsonDocument<400> status;
  status["agent_id"] = agentId;
  status["agent_name"] = agentName;
  status["wifi_connected"] = wifiConnected;
  status["ip_address"] = wifiConnected ? WiFi.localIP().toString() : "Not connected";
  status["uptime_ms"] = millis();
  status["current_tx_hash"] = currentTx.txHash;
  status["current_amount"] = currentTx.amount;
  status["transactions_received"] = txHistoryCount;
  
  Serial.print("STATUS:");
  serializeJson(status, Serial);
  Serial.println();
}

void showTransactionHistory() {
  Serial.println("=== TRANSACTION HISTORY ===");
  
  if (txHistoryCount == 0) {
    Serial.println("No transactions received yet.");
  } else {
    for (int i = 0; i < txHistoryCount; i++) {
      Serial.println("TX " + String(i + 1) + ":");
      Serial.println("  Hash: " + lastTxHistory[i].txHash);
      Serial.println("  Amount: " + String(lastTxHistory[i].amount) + " ADA");
      Serial.println("  Status: " + lastTxHistory[i].status);
      Serial.println("  Time: " + String(lastTxHistory[i].timestamp));
      Serial.println();
    }
  }
  
  Serial.println("===========================");
}

void setWiFiCredentials(String command) {
  // Parse: SET_WIFI:<ssid>:<password>
  int firstColon = command.indexOf(':', 9);
  int secondColon = command.indexOf(':', firstColon + 1);
  
  if (firstColon != -1 && secondColon != -1) {
    String newSSID = command.substring(9, firstColon);
    String newPassword = command.substring(firstColon + 1, secondColon);
    
    Serial.println("Updating WiFi credentials...");
    Serial.println("SSID: " + newSSID);
    
    // Note: In a real implementation, you'd want to store these in EEPROM
    // For now, just attempt to connect
    WiFi.begin(newSSID.c_str(), newPassword.c_str());
    
    Serial.println("WIFI_UPDATED:Attempting connection");
  }
}

void playSuccessTone() {
  // Play success melody
  tone(BUZZER_PIN, 1000, 200);
  delay(250);
  tone(BUZZER_PIN, 1500, 200);
  delay(250);
  tone(BUZZER_PIN, 2000, 300);
}

void playErrorTone() {
  // Play error melody
  tone(BUZZER_PIN, 300, 500);
  delay(600);
  tone(BUZZER_PIN, 200, 500);
}

void playConnectedTone() {
  // Play connected melody
  tone(BUZZER_PIN, 800, 200);
  delay(250);
  tone(BUZZER_PIN, 1200, 200);
  delay(250);
  tone(BUZZER_PIN, 800, 200);
}

void playAISuccessTone() {
  // Play special AI success melody - more sophisticated
  tone(BUZZER_PIN, 1000, 150);
  delay(200);
  tone(BUZZER_PIN, 1200, 150);
  delay(200);
  tone(BUZZER_PIN, 1500, 150);
  delay(200);
  tone(BUZZER_PIN, 2000, 300);  // Higher pitch for AI
  delay(350);
  tone(BUZZER_PIN, 1500, 150);
  delay(200);
  tone(BUZZER_PIN, 2000, 200);  // Ending flourish
}