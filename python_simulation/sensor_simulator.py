"""
IoT Smart Agriculture Monitoring System
File: python_simulation/sensor_simulator.py

This module generates realistic virtual sensor readings
for soil moisture, temperature, humidity, light intensity,
and water level — simulating an Arduino/ESP32 environment.
"""

import random
import time
import csv
import os
from datetime import datetime

# ─────────────────────────────────────────
#  THRESHOLD CONFIGURATION
# ─────────────────────────────────────────
THRESHOLDS = {
    "soil_dry":    400,    # Below → soil dry → pump ON
    "soil_wet":    700,    # Above → soil wet → pump OFF
    "water_low":   300,    # Below → water tank critical
    "light_low":   200,    # Below → insufficient light
    "temp_high":   35.0,   # Above → overheating alert
    "hum_low":     30.0,   # Below → humidity alert
}

# CSV output path
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "sensor_log.csv")
CSV_HEADERS = [
    "Timestamp", "Reading#",
    "Soil_Moisture", "Soil_Status",
    "Temperature_C", "Humidity_pct",
    "Water_Level", "Water_Status",
    "Light_Level", "Light_Status",
    "Pump_Status", "Alerts"
]


# ─────────────────────────────────────────
#  SENSOR SIMULATION CLASSES
# ─────────────────────────────────────────

class SoilMoistureSensor:
    """Simulates analog soil moisture sensor (0-1023 range)."""

    def __init__(self, scenario="normal"):
        self.scenario = scenario

    def read(self):
        if self.scenario == "dry":
            return random.randint(100, 380)    # Always dry
        elif self.scenario == "wet":
            return random.randint(720, 950)    # Always wet
        else:
            # Normal: fluctuates across dry/moist/wet
            return random.randint(200, 900)

    def get_status(self, value):
        if value < THRESHOLDS["soil_dry"]:
            return "DRY"
        elif value > THRESHOLDS["soil_wet"]:
            return "WET"
        return "MOIST"


class DHT11Sensor:
    """Simulates DHT11 temperature and humidity sensor."""

    def __init__(self, scenario="normal"):
        self.scenario = scenario

    def read(self):
        if self.scenario == "hot":
            temp = round(random.uniform(36.0, 42.0), 1)
            hum  = round(random.uniform(20.0, 35.0), 1)
        elif self.scenario == "cool":
            temp = round(random.uniform(15.0, 24.0), 1)
            hum  = round(random.uniform(55.0, 80.0), 1)
        else:
            temp = round(random.uniform(22.0, 38.0), 1)
            hum  = round(random.uniform(25.0, 75.0), 1)
        return temp, hum


class WaterLevelSensor:
    """Simulates analog water level sensor (0-1023 range)."""

    def __init__(self, scenario="normal"):
        self.scenario = scenario
        self._level = 700   # Starting level

    def read(self):
        if self.scenario == "draining":
            # Gradually drops
            self._level = max(50, self._level - random.randint(10, 30))
            return self._level
        elif self.scenario == "full":
            return random.randint(800, 1023)
        elif self.scenario == "low":
            return random.randint(50, 280)
        else:
            return random.randint(250, 900)

    def get_status(self, value):
        if value < THRESHOLDS["water_low"]:
            return "LOW"
        elif value > 700:
            return "FULL"
        return "MEDIUM"


class LDRSensor:
    """Simulates LDR (Light Dependent Resistor) sensor."""

    def __init__(self, scenario="normal"):
        self.scenario = scenario

    def read(self):
        if self.scenario == "dark":
            return random.randint(50, 190)
        elif self.scenario == "bright":
            return random.randint(750, 1023)
        else:
            return random.randint(100, 900)

    def get_status(self, value):
        if value < THRESHOLDS["light_low"]:
            return "DARK"
        elif value > 700:
            return "BRIGHT"
        return "NORMAL"


# ─────────────────────────────────────────
#  IRRIGATION LOGIC
# ─────────────────────────────────────────

class PumpController:
    """Controls virtual water pump based on sensor readings."""

    def __init__(self):
        self.is_on = False

    def update(self, soil_value, water_level):
        """Returns pump status string and updates internal state."""
        if soil_value < THRESHOLDS["soil_dry"] and water_level > THRESHOLDS["water_low"]:
            if not self.is_on:
                self.is_on = True
        elif soil_value >= THRESHOLDS["soil_wet"] or water_level <= THRESHOLDS["water_low"]:
            self.is_on = False

        return "ON" if self.is_on else "OFF"


# ─────────────────────────────────────────
#  ALERT ENGINE
# ─────────────────────────────────────────

def generate_alerts(temp, hum, soil, water, light):
    """Returns list of alert strings based on current readings."""
    alerts = []

    if temp > THRESHOLDS["temp_high"]:
        alerts.append(f"HIGH_TEMP({temp}C)")
    if hum < THRESHOLDS["hum_low"]:
        alerts.append(f"LOW_HUM({hum}%)")
    if soil < THRESHOLDS["soil_dry"]:
        alerts.append("DRY_SOIL")
    if water < THRESHOLDS["water_low"]:
        alerts.append("LOW_WATER_TANK")
    if light < THRESHOLDS["light_low"]:
        alerts.append("LOW_LIGHT")

    return alerts if alerts else ["NONE"]


# ─────────────────────────────────────────
#  CONSOLE DISPLAY
# ─────────────────────────────────────────

def print_reading(count, ts, soil, soil_st, temp, hum,
                  water, water_st, light, light_st, pump, alerts):
    print(f"\n{'─'*55}")
    print(f"  Reading #{count:>4}  |  {ts}")
    print(f"{'─'*55}")
    print(f"  🌱 Soil Moisture  : {soil:>4}  [{soil_st}]")
    print(f"  🌡  Temperature   : {temp:>5.1f} °C")
    print(f"  💧 Humidity       : {hum:>5.1f} %")
    print(f"  🪣 Water Level    : {water:>4}  [{water_st}]")
    print(f"  ☀  Light Level   : {light:>4}  [{light_st}]")
    print(f"  ⚙  Pump Status   : {pump}")

    if alerts != ["NONE"]:
        for a in alerts:
            print(f"  ⚠  ALERT         : {a}")
    else:
        print(f"  ✅ Status         : All normal")


# ─────────────────────────────────────────
#  CSV LOGGER
# ─────────────────────────────────────────

def init_csv():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


def log_to_csv(row_data):
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row_data)


# ─────────────────────────────────────────
#  MAIN SIMULATION LOOP
# ─────────────────────────────────────────

def run_simulation(total_readings=30, interval_sec=1.5, scenario="normal"):
    """
    Run the agriculture monitoring simulation.

    Args:
        total_readings: Number of sensor readings to simulate
        interval_sec:   Delay between readings (seconds)
        scenario:       "normal" | "dry" | "hot" | "low_water" | "mixed"
    """

    print("=" * 55)
    print("   IoT Smart Agriculture Monitoring System")
    print("   Python Simulation | Virtual Sensor Mode")
    print("=" * 55)
    print(f"  Scenario     : {scenario.upper()}")
    print(f"  Total Reads  : {total_readings}")
    print(f"  Interval     : {interval_sec}s")
    print("=" * 55)

    # Initialize sensors based on scenario
    if scenario == "dry":
        soil_sensor  = SoilMoistureSensor("dry")
        dht_sensor   = DHT11Sensor("normal")
        water_sensor = WaterLevelSensor("normal")
        ldr_sensor   = LDRSensor("normal")
    elif scenario == "hot":
        soil_sensor  = SoilMoistureSensor("dry")
        dht_sensor   = DHT11Sensor("hot")
        water_sensor = WaterLevelSensor("normal")
        ldr_sensor   = LDRSensor("bright")
    elif scenario == "low_water":
        soil_sensor  = SoilMoistureSensor("dry")
        dht_sensor   = DHT11Sensor("normal")
        water_sensor = WaterLevelSensor("draining")
        ldr_sensor   = LDRSensor("normal")
    else:  # normal / mixed
        soil_sensor  = SoilMoistureSensor("normal")
        dht_sensor   = DHT11Sensor("normal")
        water_sensor = WaterLevelSensor("normal")
        ldr_sensor   = LDRSensor("normal")

    pump = PumpController()
    init_csv()

    for i in range(1, total_readings + 1):
        ts        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        soil      = soil_sensor.read()
        soil_st   = soil_sensor.get_status(soil)
        temp, hum = dht_sensor.read()
        water     = water_sensor.read()
        water_st  = water_sensor.get_status(water)
        light     = ldr_sensor.read()
        light_st  = ldr_sensor.get_status(light)
        pump_st   = pump.update(soil, water)
        alerts    = generate_alerts(temp, hum, soil, water, light)

        # Console output
        print_reading(i, ts, soil, soil_st, temp, hum,
                      water, water_st, light, light_st,
                      pump_st, alerts)

        # CSV log
        log_to_csv([
            ts, i, soil, soil_st,
            temp, hum,
            water, water_st,
            light, light_st,
            pump_st, "|".join(alerts)
        ])

        time.sleep(interval_sec)

    print(f"\n{'='*55}")
    print(f"  Simulation complete. {total_readings} readings logged.")
    print(f"  CSV saved to: {OUTPUT_CSV}")
    print(f"{'='*55}\n")


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="IoT Smart Agriculture Sensor Simulator"
    )
    parser.add_argument(
        "--scenario",
        choices=["normal", "dry", "hot", "low_water", "mixed"],
        default="normal",
        help="Simulation scenario (default: normal)"
    )
    parser.add_argument(
        "--readings",
        type=int,
        default=20,
        help="Number of sensor readings (default: 20)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between readings (default: 1.0)"
    )

    args = parser.parse_args()
    run_simulation(
        total_readings=args.readings,
        interval_sec=args.interval,
        scenario=args.scenario
    )
