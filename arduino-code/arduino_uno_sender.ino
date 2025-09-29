// Arduino Uno Code for Masumi Network Integration
// Receives commands from PC via Serial and processes payments

#include <ArduinoJson.h>

// Pin definitions
const int LED_PIN = 13;           // Built-in LED for status
const int BUTTON_PIN = 2;         // Digital pin 2 for payment trigger
const int STATUS_LED_PIN = 8;     // External LED for transaction status

// Agent configuration
String agentId = "arduino_uno_001";
String agentName = "Arduino Sender";
bool isConnected = false;
unsigned long lastHeartbeat = 0;
unsigned long buttonPressTime = 0;
bool buttonPressed = false;

// Transaction variables
String currentTxHash = "";
float lastAmount = 0;
String lastStatus = "";

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Flash LED to indicate startup
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
  
  Serial.println("=== Arduino Masumi Network Node ===");
  Serial.println("Agent ID: " + agentId);
  Serial.println("Agent Name: " + agentName);
  Serial.println("Ready for PC commands...");
  Serial.println("Commands: SEND_PAYMENT:<amount>:<recipient>");
  Serial.println("          GET_STATUS");
  Serial.println("          HEARTBEAT");
  Serial.println("======================================");
  
  // Initialize connection status
  isConnected = true;
  digitalWrite(STATUS_LED_PIN, HIGH);
}

void loop() {
  // Check for serial commands from PC
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processSerialCommand(command);
  }
  
  // Check physical button for manual payment trigger
  checkPaymentButton();
  
  // Send heartbeat every 5 seconds
  if (millis() - lastHeartbeat > 5000) {
    sendHeartbeat();
    lastHeartbeat = millis();
  }
  
  // Blink status LED if connected
  if (isConnected) {
    blinkStatusLED();
  }
  
  delay(100);
}

void processSerialCommand(String command) {
  Serial.println("Received: " + command);
  
  if (command.startsWith("SEND_PAYMENT:")) {
    processSendPayment(command);
  }
  else if (command == "GET_STATUS") {
    sendStatus();
  }
  else if (command == "HEARTBEAT") {
    respondHeartbeat();
  }
  else if (command.startsWith("SET_AGENT:")) {
    setAgentInfo(command);
  }
  else if (command.startsWith("AI_SUCCESS:")) {
    processAISuccess(command);
  }
  else if (command.startsWith("AI_DECLINED:")) {
    processAIDeclined(command);
  }
  else if (command.startsWith("AI_FAILED:") || command.startsWith("AI_ERROR:")) {
    processAIError(command);
  }
  else if (command.startsWith("AI_TRANSACTION:")) {
    processAITransaction(command);
  }
  else {
    Serial.println("ERROR: Unknown command - " + command);
  }
}

void processSendPayment(String command) {
  // Parse: SEND_PAYMENT:<amount>:<recipient>
  int firstColon = command.indexOf(':', 12);
  int secondColon = command.indexOf(':', firstColon + 1);
  
  if (firstColon == -1 || secondColon == -1) {
    Serial.println("ERROR: Invalid payment command format");
    return;
  }
  
  float amount = command.substring(12, firstColon).toFloat();
  String recipient = command.substring(firstColon + 1, secondColon);
  
  if (amount <= 0) {
    Serial.println("ERROR: Invalid amount");
    return;
  }
  
  Serial.println("Processing payment:");
  Serial.println("  Amount: " + String(amount) + " ADA");
  Serial.println("  Recipient: " + recipient);
  Serial.println("  From: " + agentId);
  
  // Simulate payment processing
  digitalWrite(LED_PIN, HIGH);
  Serial.println("STATUS: Initiating Cardano transaction...");
  
  delay(1000); // Simulate processing time
  
  Serial.println("STATUS: Connecting to Masumi Network...");
  delay(500);
  
  Serial.println("STATUS: Broadcasting transaction...");
  delay(1000);
  
  // Store transaction info
  lastAmount = amount;
  
  Serial.println("STATUS: Transaction initiated successfully");
  Serial.println("PAYMENT_INITIATED:" + String(amount) + ":" + recipient);
  Serial.println("COMPLETE");
  
  digitalWrite(LED_PIN, LOW);
  
  // Flash status LED to indicate transaction
  for (int i = 0; i < 5; i++) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(100);
  }
  digitalWrite(STATUS_LED_PIN, HIGH);
}

void checkPaymentButton() {
  // Check if button is pressed (pulled low)
  if (digitalRead(BUTTON_PIN) == LOW && !buttonPressed) {
    buttonPressed = true;
    buttonPressTime = millis();
    
    Serial.println("BUTTON_PRESSED: Triggering Satoshi AI Agent Decision");
    Serial.println("🤖 AI Agent will analyze market conditions and decide...");
    
    // Flash LED to indicate AI processing
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
      delay(100);
    }
  }
  
  // Reset button state after release
  if (digitalRead(BUTTON_PIN) == HIGH && buttonPressed) {
    if (millis() - buttonPressTime > 50) { // Debounce
      buttonPressed = false;
    }
  }
}

void processAISuccess(String command) {
  // Parse: AI_SUCCESS:<amount>:<tx_hash>
  int firstColon = command.indexOf(':', 11);
  int secondColon = command.indexOf(':', firstColon + 1);
  
  if (firstColon != -1 && secondColon != -1) {
    float amount = command.substring(11, firstColon).toFloat();
    String txHashShort = command.substring(firstColon + 1, secondColon);
    
    Serial.println("🎉 SATOSHI AI AGENT SUCCESS! 🎉");
    Serial.println("AI Agent executed autonomous transaction:");
    Serial.println("  Amount: " + String(amount) + " ADA");
    Serial.println("  TX Hash: " + txHashShort + "...");
    Serial.println("  Decision: AI approved based on market analysis");
    
    lastAmount = amount;
    currentTxHash = txHashShort + "...";
    
    // Success celebration pattern
    for (int i = 0; i < 5; i++) {
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_PIN, LOW);
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(200);
    }
    
    Serial.println("AI_TRANSACTION_COMPLETE");
  }
}

void processAIDeclined(String command) {
  // Parse: AI_DECLINED:<confidence>:<reason>
  int firstColon = command.indexOf(':', 12);
  int secondColon = command.indexOf(':', firstColon + 1);
  
  if (firstColon != -1) {
    float confidence = command.substring(12, firstColon).toFloat();
    String reason = secondColon != -1 ? command.substring(firstColon + 1, secondColon) : "UNKNOWN";
    
    Serial.println("🤔 AI AGENT DECLINED TRANSACTION");
    Serial.println("AI Agent decision: NO TRANSACTION");
    Serial.println("  Confidence: " + String(confidence, 2));
    Serial.println("  Reason: " + reason);
    Serial.println("  Analysis: Market conditions not favorable");
    
    // Declined pattern - slow blink
    for (int i = 0; i < 3; i++) {
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(500);
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(500);
    }
    
    Serial.println("AI_DECISION_COMPLETE");
  }
}

void processAIError(String command) {
  Serial.println("❌ AI AGENT ERROR");
  Serial.println("AI Agent encountered an error during decision process");
  Serial.println("Command: " + command);
  
  // Error pattern - fast blink
  for (int i = 0; i < 10; i++) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(50);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(50);
  }
  
  Serial.println("AI_ERROR_HANDLED");
}

void processAITransaction(String command) {
  // Parse: AI_TRANSACTION:<agent_id>:<amount>:<tx_hash_short>
  int firstColon = command.indexOf(':', 15);
  int secondColon = command.indexOf(':', firstColon + 1);
  int thirdColon = command.indexOf(':', secondColon + 1);
  
  if (firstColon != -1 && secondColon != -1 && thirdColon != -1) {
    String agentId = command.substring(15, firstColon);
    float amount = command.substring(firstColon + 1, secondColon).toFloat();
    String txHash = command.substring(secondColon + 1, thirdColon);
    
    Serial.println("🤖 AUTONOMOUS AI TRANSACTION DETECTED");
    Serial.println("Agent: " + agentId);
    Serial.println("Amount: " + String(amount) + " ADA");
    Serial.println("TX: " + txHash + "...");
    Serial.println("Type: Fully Autonomous AI Decision");
    
    lastAmount = amount;
    currentTxHash = txHash + "...";
    
    // AI transaction pattern - unique sequence
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(50);
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(50);
    
    // Repeat pattern 3 times
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(150);
      digitalWrite(LED_PIN, LOW);
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(150);
    }
    
    Serial.println("AI_AUTONOMOUS_TX_PROCESSED");
  }
}

void sendHeartbeat() {
  StaticJsonDocument<200> heartbeat;
  heartbeat["type"] = "heartbeat";
  heartbeat["agent_id"] = agentId;
  heartbeat["timestamp"] = millis();
  heartbeat["status"] = isConnected ? "connected" : "disconnected";
  heartbeat["last_tx_amount"] = lastAmount;
  
  Serial.print("HEARTBEAT:");
  serializeJson(heartbeat, Serial);
  Serial.println();
}

void respondHeartbeat() {
  Serial.println("HEARTBEAT_ACK:" + agentId + ":ONLINE");
}

void sendStatus() {
  StaticJsonDocument<300> status;
  status["agent_id"] = agentId;
  status["agent_name"] = agentName;
  status["connected"] = isConnected;
  status["uptime_ms"] = millis();
  status["last_tx_hash"] = currentTxHash;
  status["last_amount"] = lastAmount;
  status["button_state"] = digitalRead(BUTTON_PIN) == LOW ? "pressed" : "released";
  
  Serial.print("STATUS:");
  serializeJson(status, Serial);
  Serial.println();
}

void setAgentInfo(String command) {
  // Parse: SET_AGENT:<agent_id>:<agent_name>
  int firstColon = command.indexOf(':', 10);
  int secondColon = command.indexOf(':', firstColon + 1);
  
  if (firstColon != -1) {
    agentId = command.substring(10, firstColon);
    if (secondColon != -1) {
      agentName = command.substring(firstColon + 1, secondColon);
    }
    Serial.println("AGENT_UPDATED:" + agentId + ":" + agentName);
  }
}

void blinkStatusLED() {
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  
  if (millis() - lastBlink > 2000) {
    ledState = !ledState;
    digitalWrite(STATUS_LED_PIN, ledState);
    lastBlink = millis();
  }
}

// Helper function for debugging
void printAgentInfo() {
  Serial.println("=== Agent Information ===");
  Serial.println("ID: " + agentId);
  Serial.println("Name: " + agentName);
  Serial.println("Connected: " + String(isConnected ? "Yes" : "No"));
  Serial.println("Uptime: " + String(millis() / 1000) + " seconds");
  Serial.println("========================");
}