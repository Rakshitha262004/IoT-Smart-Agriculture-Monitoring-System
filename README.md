# 🌿 IoT-Enabled Smart Agriculture Monitoring System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Arduino](https://img.shields.io/badge/Arduino-UNO%2FESP32-teal?style=for-the-badge&logo=arduino)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![IoT](https://img.shields.io/badge/Domain-IoT%20%7C%20Smart%20Agriculture-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A complete IoT simulation system that monitors soil moisture, temperature, humidity, light intensity, and water level — with automated irrigation control and a real-time Streamlit dashboard.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [How to Run](#-how-to-run) • [Screenshots](#-screenshots) • [Interview Prep](#-interview-preparation)

</div>

---

## 📌 Problem Statement

Traditional farming relies on manual observation to decide when to irrigate, often leading to overwatering, underwatering, or delayed response to extreme weather — all of which reduce crop yield and waste precious water resources.

This project solves the problem by building an IoT-based system that:
- Continuously monitors five environmental parameters
- Automatically triggers irrigation when soil is dry
- Alerts farmers to critical conditions (high heat, low water tank, etc.)
- Logs all sensor data for analysis and reporting

---

## 💡 Simple Explanation

> Imagine placing tiny sensors in a field that measure how dry the soil is, how hot it is, and how much water is in the tank — then automatically turning on a water pump when needed, and sending you alerts if anything is wrong. That is exactly what this system does.

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   SENSOR LAYER (INPUT)                   │
│  🌱 Soil Moisture  🌡 DHT11  🪣 Water Level  ☀ LDR       │
└──────────────────┬───────────────────────────────────────┘
                   │ Analog/Digital readings
                   ▼
┌──────────────────────────────────────────────────────────┐
│               PROCESSING LAYER                           │
│   Arduino UNO / ESP32 / Python Simulation                │
│   • Read sensor values every 2 seconds                   │
│   • Compare against defined thresholds                   │
│   • Make irrigation decision (pump ON/OFF)               │
│   • Generate alert messages                              │
└──────────────────┬───────────────────────────────────────┘
                   │ Processed data
                   ▼
┌──────────────────────────────────────────────────────────┐
│               OUTPUT LAYER                               │
│   📊 Streamlit Dashboard   📋 CSV Log   🔔 Alerts        │
│   ⚙ Pump Relay ON/OFF      🖥 Serial Monitor             │
└──────────────────────────────────────────────────────────┘
```

**Sensor Data Flow:**
```
Soil Moisture (A0) ──┐
Temperature (DHT11) ──┤
Humidity (DHT11)    ──┤──→ Threshold Check ──→ Pump ON/OFF (Relay pin 7)
Water Level (A1)    ──┤         │
Light Intensity (A2)──┘         └──→ Alert Engine ──→ Serial / Dashboard
```

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 🌱 **Soil Monitoring** | Real-time soil moisture tracking with DRY / MOIST / WET status |
| 🌡️ **Climate Tracking** | Temperature and humidity via DHT11 sensor |
| 🪣 **Water Management** | Water tank level monitoring with low-water alerts |
| ☀️ **Light Sensing** | LDR-based light intensity for greenhouse control |
| ⚙️ **Auto Irrigation** | Pump auto-activates when soil is dry (relay control) |
| 🔔 **Alert System** | Multi-level alerts for all critical conditions |
| 📊 **Live Dashboard** | Streamlit dashboard with Plotly charts and metric cards |
| 📋 **Data Logging** | All readings saved to CSV for analysis |
| 🐍 **Virtual Simulation** | Run without hardware using Python sensor simulator |
| 🎭 **Scenario Testing** | Dry / Hot / Low-Water / Normal simulation modes |

---

## 🛠 Tech Stack

### Hardware (Physical or Simulated)
- Arduino UNO / ESP32
- DHT11 (Temperature + Humidity)
- FC-28 Soil Moisture Sensor
- LDR (Light Dependent Resistor)
- Water Level Sensor
- 5V Relay Module + Mini Water Pump

### Software
- **Arduino IDE** — Microcontroller code
- **Wokwi** — Online Arduino simulation
- **Python 3.8+** — Sensor simulation
- **Streamlit** — Real-time dashboard
- **Plotly** — Interactive charts
- **Pandas** — Data logging

---

## 📁 Folder Structure

```
IoT-Smart-Agriculture-Monitoring-System/
│
├── arduino_code/
│   └── smart_agriculture.ino    # Arduino sensor + pump control code
│
├── python_simulation/
│   └── sensor_simulator.py      # Virtual sensor with 5 scenarios
│
├── dashboard/
│   └── app.py                   # Streamlit real-time dashboard
│
├── data/
│   └── sensor_log.csv           # Auto-generated sensor log
│
├── outputs/
│   └── (simulation output screenshots)
│
├── images/
│   └── (architecture diagrams, screenshots)
│
├── circuit_diagram/
│   └── (Wokwi/Tinkercad screenshots)
│
├── docs/
│   └── project_explanation.md
│
├── main.py                      # Project entry point
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Rakshitha262004/IoT-Smart-Agriculture-Monitoring-System.git
cd IoT-Smart-Agriculture-Monitoring-System

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run simulation + dashboard
python main.py --scenario dry --readings 30
```

---

## 🚀 How to Run

### Option A: Python Simulation (No Hardware Required)

```bash
# Normal scenario
python python_simulation/sensor_simulator.py

# Dry soil scenario (pump activates)
python python_simulation/sensor_simulator.py --scenario dry --readings 30

# High temperature scenario
python python_simulation/sensor_simulator.py --scenario hot --readings 20

# Draining water tank
python python_simulation/sensor_simulator.py --scenario low_water --readings 25
```

### Option B: Streamlit Dashboard

```bash
# First generate sensor data
python python_simulation/sensor_simulator.py --scenario dry --readings 30

# Then launch dashboard
streamlit run dashboard/app.py
```

Open browser: `http://localhost:8501`

### Option C: Arduino / Wokwi Simulation

1. Open [wokwi.com](https://wokwi.com)
2. Create new **Arduino UNO** project
3. Add components: DHT11, Potentiometers (x3 simulating analog sensors), LED
4. Paste code from `arduino_code/smart_agriculture.ino`
5. Run simulation and observe Serial Monitor

---

## 📊 Sample Output

```
═══════════════════════════════════════════════════════
   IoT Smart Agriculture Monitoring System
   Python Simulation | Virtual Sensor Mode
═══════════════════════════════════════════════════════
  Scenario     : DRY
  Total Reads  : 20
═══════════════════════════════════════════════════════

─── Reading #  1 ──────────────────────────────────────
  🌱 Soil Moisture  :  250  [DRY]
  🌡  Temperature   :  28.4 °C
  💧 Humidity       :  55.2 %
  🪣 Water Level    :  680  [FULL]
  ☀  Light Level   :  540  [NORMAL]
  ⚙  Pump Status   : ON
  ⚠  ALERT         : DRY_SOIL
```

---

## 🔌 Circuit Diagram (Wokwi Simulation)

| Component | Arduino Pin |
|-----------|-------------|
| DHT11 Data | Digital Pin 2 |
| Soil Sensor | Analog Pin A0 |
| Water Level | Analog Pin A1 |
| LDR Sensor | Analog Pin A2 |
| Relay (Pump) | Digital Pin 7 |
| Alert LED | Digital Pin 13 |
| VCC | 5V |
| GND | GND |

---

## 🎯 IoT Concepts Demonstrated

1. **Sensor Integration** — Reading analog + digital sensors
2. **Threshold-based Control** — Automated decision logic
3. **Actuator Control** — Relay/pump ON-OFF
4. **Data Logging** — Continuous CSV logging
5. **Edge Processing** — On-device decision making
6. **Alert Generation** — Real-time fault detection
7. **Dashboard Visualization** — IoT data monitoring
8. **Simulation** — Virtual environment testing

---

## 📈 Learning Outcomes

After completing this project you will understand:
- How IoT sensors connect to microcontrollers
- How to design threshold-based automation logic
- How to simulate IoT systems without hardware
- How to build real-time IoT dashboards with Streamlit
- How to log and analyze time-series sensor data
- How smart agriculture reduces water waste and improves yield

---

## 🤝 Author

**Rakshitha** — B.E. Cybersecurity, ACS College of Engineering, Bengaluru  
GitHub: [github.com/Rakshitha262004](https://github.com/Rakshitha262004)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
