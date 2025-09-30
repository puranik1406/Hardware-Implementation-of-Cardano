# Hardware Wiring

## Arduino Uno

- Button: one leg to D2, other leg to GND; enable INPUT_PULLUP in code
- LEDs: OK → D13, BUSY → D12, ERR → D11 (series resistor ~220Ω to GND)
- USB to PC for serial (115200 or 9600 per sketch)

## ESP8266 (NodeMCU)

- I2C LCD 16x2: SDA → D2, SCL → D1, VCC → 5V, GND → GND
- Update WiFi SSID/PASS and PC_HOST in `hardware/esp8266/transaction_display.ino`
- Ensure PC firewall allows inbound from ESP8266 to port 3001

## Notes

- On Windows, find the Arduino COM port in Arduino IDE → Tools → Port
- Use quality USB cables and stable 5V power