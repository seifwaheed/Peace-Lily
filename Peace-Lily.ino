/*
 * Talking Plant Project - ESP32 Complete Sensor Code
 * Reads DHT22 (temperature & humidity) and soil moisture (capacitive)
 * 
 * Hardware:
 * - ESP32 microcontroller
 * - DHT22 sensor on GPIO 4
 * - Capacitive soil moisture sensor on GPIO 35 (analog)
 * 
 * Serial Output Format: TEMP:XX.X,HUM:XX.X,MOIST:XX
 * Baud Rate: 115200
 */

#include <SimpleDHT.h>

// Pin definitions
#define DHT_PIN 4            // DHT22 data pin
#define MOISTURE_PIN 35      // Moisture sensor analog pin

// DHT22 sensor object
SimpleDHT22 dht22(DHT_PIN);

// ====== CHANGE THESE AFTER CALIBRATION ======
// Example values (replace with your real measurements)
// ====== CHANGE THESE AFTER CALIBRATION ======
const int dryValue = 3000;   // Sensor in air (dry) → maps to 0%
const int wetValue = 1700;   // Sensor fully wet (watered) → maps to 100%
// ============================================
// ============================================

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("\n\n=== TALKING PLANT PROJECT ===");
  Serial.println("ESP32 Complete Sensor Monitor");
  Serial.println("DHT22 on GPIO 4");
  Serial.println("Moisture Sensor on GPIO 35");
  Serial.println("=====================================\n");
}

void loop() {
  // Read DHT22 sensor
  float temperature = 0;
  float humidity = 0;
  int err = SimpleDHTErrSuccess;

  if ((err = dht22.read2(&temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
    Serial.print("[DHT22 ERROR] Code: ");
    Serial.println(err);
    delay(2000);
    return;
  }

  // Read moisture sensor
  int rawMoisture = analogRead(MOISTURE_PIN);

  // Convert to 0–100% range
  int moisturePercent = map(rawMoisture, dryValue, wetValue, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);

  // Output formatted data
  Serial.print("TEMP:");
  Serial.print(temperature, 1);
  Serial.print(",HUM:");
  Serial.print(humidity, 1);
  Serial.print(",MOIST:");
  Serial.println(moisturePercent);

  // Debug info
  Serial.print("[DEBUG] DHT22: ");
  Serial.print(temperature, 1);
  Serial.print("°C, ");
  Serial.print(humidity, 1);
  Serial.print("% | Moisture Raw: ");
  Serial.print(rawMoisture);
  Serial.print(" → ");
  Serial.print(moisturePercent);
  Serial.println("%");

  delay(5000);
}
