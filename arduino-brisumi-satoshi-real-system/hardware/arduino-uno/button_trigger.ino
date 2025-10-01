/*
 * Arduino Uno #1 - Payment Trigger (COM6)
 * Hardware: Button on Pin 2 ONLY
 * Purpose: Trigger payment requests when button is pressed
 */

const int BUTTON_PIN = 2;

volatile bool buttonPressed = false;
bool waitingForResponse = false;

void setup() {
  // Initialize button pin
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Attach interrupt for button
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonISR, FALLING);
  
  // Start serial communication
  Serial.begin(9600);
  
  Serial.println("READY");
  Serial.println("Arduino Button Trigger initialized on COM6");
}

void buttonISR() {
  // Simple debounce - set flag
  if (!waitingForResponse) {
    buttonPressed = true;
  }
}

void loop() {
  // Handle button press
  if (buttonPressed && !waitingForResponse) {
    buttonPressed = false;
    triggerPayment();
  }
  
  // Listen for responses from PC (for confirmation)
  if (Serial.available() > 0) {
    String response = Serial.readStringUntil('\n');
    response.trim();
    handleResponse(response);
  }
  
  delay(10); // Small delay to prevent serial flooding
}

void triggerPayment() {
  // Send payment trigger command to PC
  Serial.println("TRIGGER_PAYMENT");
  Serial.println("FROM_AGENT:satoshi_alpha_001");
  Serial.println("TO_AGENT:satoshi_beta_002");
  Serial.println("AMOUNT:1");
  Serial.println("EMOTION:I am so happy and excited about this amazing blockchain transaction!");
  Serial.println("END_COMMAND");
  
  waitingForResponse = true;
}

void handleResponse(String response) {
  // Just acknowledge and reset state
  if (response.startsWith("TX:") || response == "REJECTED" || response == "ERROR") {
    waitingForResponse = false;
  }
}
