/*
 * IoT-Enabled Smart Agriculture Monitoring System
 * File: smart_agriculture.ino
 * Platform: Arduino UNO / ESP32
 * Sensors: DHT11, Soil Moisture, LDR, Water Level
 * Author: Rakshitha (2025)
 *
 * This code reads sensor data, checks thresholds,
 * controls a water pump relay, and prints alerts
 * to the Serial Monitor.
 */

#include <DHT.h>

// ─────────────────────────────────────────
//  PIN DEFINITIONS
// ─────────────────────────────────────────
#define DHT_PIN        2      // DHT11 data pin
#define DHT_TYPE       DHT11

#define SOIL_PIN       A0     // Soil moisture sensor (analog)
#define WATER_PIN      A1     // Water level sensor (analog)
#define LDR_PIN        A2     // Light sensor / LDR (analog)
#define RELAY_PIN      7      // Relay / pump control (digital)
#define LED_ALERT_PIN  13     // Built-in LED for alert

// ─────────────────────────────────────────
//  THRESHOLD CONSTANTS
// ─────────────────────────────────────────
const int  SOIL_DRY_THRESHOLD   = 400;  // Below this → soil is dry → pump ON
const int  SOIL_WET_THRESHOLD   = 700;  // Above this → soil is wet → pump OFF
const int  WATER_LOW_THRESHOLD  = 300;  // Below this → water tank is low → alert
const int  LIGHT_LOW_THRESHOLD  = 200;  // Below this → not enough light
const float TEMP_HIGH_THRESHOLD = 35.0; // Above this → too hot → alert
const float HUM_LOW_THRESHOLD   = 30.0; // Below this → humidity low → alert

// ─────────────────────────────────────────
//  GLOBALS
// ─────────────────────────────────────────
DHT dht(DHT_PIN, DHT_TYPE);

bool pumpStatus      = false;
int  readingCounter  = 0;
unsigned long lastReadTime = 0;
const long READ_INTERVAL   = 2000; // Read every 2 seconds

// ─────────────────────────────────────────
//  SETUP
// ─────────────────────────────────────────
void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_ALERT_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);    // Pump OFF at start
  digitalWrite(LED_ALERT_PIN, LOW);

  Serial.println("=========================================");
  Serial.println("  IoT Smart Agriculture Monitoring System");
  Serial.println("=========================================");
  Serial.println("System Initialized. Starting sensor loop...");
  Serial.println();
}

// ─────────────────────────────────────────
//  MAIN LOOP
// ─────────────────────────────────────────
void loop() {
  unsigned long currentTime = millis();

  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    readingCounter++;

    // 1. Read all sensors
    float temperature  = dht.readTemperature();
    float humidity     = dht.readHumidity();
    int   soilValue    = analogRead(SOIL_PIN);
    int   waterLevel   = analogRead(WATER_PIN);
    int   lightLevel   = analogRead(LDR_PIN);

    // 2. Guard against bad DHT readings
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("[ERROR] DHT sensor read failed. Retrying...");
      return;
    }

    // 3. Print sensor header
    Serial.print("─── Reading #");
    Serial.print(readingCounter);
    Serial.println(" ──────────────────────────");

    // 4. Print sensor values
    printSensorValues(temperature, humidity, soilValue, waterLevel, lightLevel);

    // 5. Check thresholds and control pump
    checkAndControlPump(soilValue, waterLevel);

    // 6. Generate alerts
    generateAlerts(temperature, humidity, soilValue, waterLevel, lightLevel);

    // 7. Print pump status
    Serial.print("  [PUMP]  Status : ");
    Serial.println(pumpStatus ? "ON  (Irrigation Active)" : "OFF (Soil Moisture OK)");
    Serial.println();
  }
}

// ─────────────────────────────────────────
//  FUNCTION: Print Sensor Values
// ─────────────────────────────────────────
void printSensorValues(float temp, float hum, int soil, int water, int light) {
  Serial.print("  [TEMP]  Temperature  : ");
  Serial.print(temp, 1);
  Serial.println(" °C");

  Serial.print("  [HUM]   Humidity     : ");
  Serial.print(hum, 1);
  Serial.println(" %");

  Serial.print("  [SOIL]  Soil Moisture: ");
  Serial.print(soil);
  Serial.print(" (");
  Serial.print(getSoilStatus(soil));
  Serial.println(")");

  Serial.print("  [WATER] Water Level  : ");
  Serial.print(water);
  Serial.print(" (");
  Serial.print(getWaterStatus(water));
  Serial.println(")");

  Serial.print("  [LIGHT] Light Level  : ");
  Serial.print(light);
  Serial.print(" (");
  Serial.print(getLightStatus(light));
  Serial.println(")");
}

// ─────────────────────────────────────────
//  FUNCTION: Pump Control Logic
// ─────────────────────────────────────────
void checkAndControlPump(int soilValue, int waterLevel) {
  // Turn pump ON if soil is dry AND water tank has water
  if (soilValue < SOIL_DRY_THRESHOLD && waterLevel > WATER_LOW_THRESHOLD) {
    if (!pumpStatus) {
      pumpStatus = true;
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("  [ACTION] Pump turned ON  — Soil dry, irrigation started.");
    }
  }
  // Turn pump OFF if soil is wet OR water tank is empty
  else if (soilValue >= SOIL_WET_THRESHOLD || waterLevel <= WATER_LOW_THRESHOLD) {
    if (pumpStatus) {
      pumpStatus = false;
      digitalWrite(RELAY_PIN, LOW);
      if (waterLevel <= WATER_LOW_THRESHOLD) {
        Serial.println("  [ACTION] Pump turned OFF — Water tank low!");
      } else {
        Serial.println("  [ACTION] Pump turned OFF — Soil moisture sufficient.");
      }
    }
  }
}

// ─────────────────────────────────────────
//  FUNCTION: Alert Generation
// ─────────────────────────────────────────
void generateAlerts(float temp, float hum, int soil, int water, int light) {
  bool alertTriggered = false;

  if (temp > TEMP_HIGH_THRESHOLD) {
    Serial.println("  ⚠ ALERT: High Temperature! Consider shade or cooling.");
    alertTriggered = true;
  }
  if (hum < HUM_LOW_THRESHOLD) {
    Serial.println("  ⚠ ALERT: Low Humidity! Crops may stress.");
    alertTriggered = true;
  }
  if (soil < SOIL_DRY_THRESHOLD) {
    Serial.println("  ⚠ ALERT: Soil is DRY. Irrigation recommended.");
    alertTriggered = true;
  }
  if (water < WATER_LOW_THRESHOLD) {
    Serial.println("  ⚠ ALERT: Water tank level is LOW. Refill needed!");
    alertTriggered = true;
  }
  if (light < LIGHT_LOW_THRESHOLD) {
    Serial.println("  ⚠ ALERT: Low light intensity. Check for cloud cover.");
    alertTriggered = true;
  }

  // Blink alert LED if any alert
  if (alertTriggered) {
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_ALERT_PIN, HIGH);
      delay(100);
      digitalWrite(LED_ALERT_PIN, LOW);
      delay(100);
    }
  }
}

// ─────────────────────────────────────────
//  HELPER: Soil Status Label
// ─────────────────────────────────────────
String getSoilStatus(int val) {
  if (val < SOIL_DRY_THRESHOLD)  return "DRY";
  if (val > SOIL_WET_THRESHOLD)  return "WET";
  return "MOIST";
}

// ─────────────────────────────────────────
//  HELPER: Water Level Label
// ─────────────────────────────────────────
String getWaterStatus(int val) {
  if (val < WATER_LOW_THRESHOLD) return "LOW";
  if (val > 600)                 return "FULL";
  return "MEDIUM";
}

// ─────────────────────────────────────────
//  HELPER: Light Level Label
// ─────────────────────────────────────────
String getLightStatus(int val) {
  if (val < LIGHT_LOW_THRESHOLD) return "DARK";
  if (val > 700)                 return "BRIGHT";
  return "NORMAL";
}
