// Arduino Uno – Payment Trigger
// Button on pin 2, LEDs on pins 11-13

const int BUTTON_PIN = 2;
const int LED_OK = 13;
const int LED_BUSY = 12;
const int LED_ERR = 11;

volatile bool buttonPressed = false;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_OK, OUTPUT);
  pinMode(LED_BUSY, OUTPUT);
  pinMode(LED_ERR, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), onButton, FALLING);
  Serial.begin(9600);
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
    delay(50);
    Serial.println("TRIGGER_PAYMENT");
  Serial.println("FROM_AGENT:satoshi-1");
  Serial.println("TO_AGENT:satoshi-2");
  Serial.println("AMOUNT:1");
    Serial.println("END_COMMAND");
    // Wait for response line like TX:...
    unsigned long start = millis();
    while (millis() - start < 5000) {
      if (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        if (line.startsWith("TX:")) {
          digitalWrite(LED_OK, HIGH);
          delay(500);
          digitalWrite(LED_OK, LOW);
          break;
        }
      }
    }
    digitalWrite(LED_BUSY, LOW);
  }
}
