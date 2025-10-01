// Arduino Uno #1 – Payment Trigger with Emotional Context
// COM6 - Button Trigger with Emotional AI Integration
// Button on pin 2, LEDs on pins 8 (Green), 9 (Red)

const int BUTTON_PIN = 2;
const int LED_OK = 8;      // Green LED - Approved
const int LED_ERR = 9;     // Red LED - Rejected

volatile bool buttonPressed = false;
bool waitingForResponse = false;

// Emotional contexts (cycles through on each button press)
const char* emotions[] = {
  "I am so happy and excited about this blockchain transaction!",
  "I am feeling great and confident about this payment!",
  "This is an amazing project and I love using it!",
  "I am very angry and frustrated about this situation!",
  "This is terrible and I do not want to proceed!"
};
int emotionIndex = 0;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_OK, OUTPUT);
  pinMode(LED_ERR, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), onButton, FALLING);
  Serial.begin(9600);
  
  digitalWrite(LED_OK, LOW);
  digitalWrite(LED_ERR, LOW);
  
  // Startup blink
  for(int i = 0; i < 3; i++) {
    digitalWrite(LED_OK, HIGH);
    digitalWrite(LED_ERR, HIGH);
    delay(200);
    digitalWrite(LED_OK, LOW);
    digitalWrite(LED_ERR, LOW);
    delay(200);
  }
  
  Serial.println("Arduino Ready (COM6)");
}

void onButton() {
  buttonPressed = true;
}

void loop() {
  if (buttonPressed && !waitingForResponse) {
    buttonPressed = false;
    
    // Blink both LEDs
    for(int i = 0; i < 2; i++) {
      digitalWrite(LED_OK, HIGH);
      digitalWrite(LED_ERR, HIGH);
      delay(100);
      digitalWrite(LED_OK, LOW);
      digitalWrite(LED_ERR, LOW);
      delay(100);
    }
    
    // Send payment with emotional context
    Serial.println("TRIGGER_PAYMENT");
    Serial.println("FROM_AGENT:satoshi_alpha_001");
    Serial.println("TO_AGENT:satoshi_beta_002");
    Serial.println("AMOUNT:1");
    Serial.print("EMOTION:");
    Serial.println(emotions[emotionIndex]);
    Serial.println("END_COMMAND");
    
    emotionIndex = (emotionIndex + 1) % 5;
    waitingForResponse = true;
  }
  
  // Check for responses
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.startsWith("TX:")) {
      // Success - Green LED
      digitalWrite(LED_OK, HIGH);
      digitalWrite(LED_ERR, LOW);
      delay(3000);
      digitalWrite(LED_OK, LOW);
      waitingForResponse = false;
    } 
    else if (line == "REJECTED") {
      // Rejected - Red LED blinks
      digitalWrite(LED_OK, LOW);
      for(int i = 0; i < 5; i++) {
        digitalWrite(LED_ERR, HIGH);
        delay(200);
        digitalWrite(LED_ERR, LOW);
        delay(200);
      }
      waitingForResponse = false;
    }
  }
}
