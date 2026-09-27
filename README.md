# ⚡ WattWise AI

## An Explainable Energy Waste Copilot for Hostels & Small Offices

WattWise AI is a prototype energy intelligence platform designed to help hostels and small offices understand **where energy may be wasted, why the pattern is unusual, what action can be taken, and how much energy or cost could potentially be saved**.

Instead of simply displaying electricity consumption, WattWise combines energy usage with contextual information such as **occupancy, temperature, device status, schedules, and anomaly signals** to provide explainable energy insights.

> ⚠️ **Prototype Notice:** The current demonstration uses simulated smart-meter/context data. The reported savings and WattWise Score are prototype calculations and are not verified real-world measurements.

---

## 🎯 Problem

Small hostels and offices often know how much electricity they consume, but not:

- Where unnecessary consumption is happening
- Whether high consumption is actually abnormal
- Why a particular energy event may be wasteful
- What action could reduce the waste
- Whether a proposed intervention could reduce energy and cost

Existing dashboards often focus mainly on **monitoring**.

WattWise AI focuses on **understanding and action**.

---

## 💡 Solution

WattWise AI acts as an **explainable energy waste copilot**.

It follows a simple workflow:

**Detect → Explain → Recommend → Simulate → Verify**

### 1. Detect
Identifies potentially wasteful energy events using contextual rules and machine-learning anomaly detection.

### 2. Explain
Provides a human-readable explanation for why an event was flagged.

### 3. Recommend
Suggests a practical action based on the detected pattern.

### 4. Simulate
Uses a What-If simulator to estimate potential energy and cost savings under different waste-prevention scenarios.

### 5. Verify
The intended future deployment can compare actual before-and-after energy data to verify whether an intervention produced real savings.

---

## 🧠 AI & Intelligence

WattWise uses a hybrid approach.

### Context-Based Detection

Domain rules identify patterns such as:

- AC running while occupancy is zero
- Unoccupied rooms consuming unusually high power

### Machine-Learning Anomaly Detection

An **Isolation Forest** model identifies unusual combinations of:

- Temperature
- Occupancy
- AC status
- Light status
- Schedule
- Power consumption

An anomaly is not automatically treated as waste. It is marked for **contextual review**.

This distinction helps avoid treating every unusual energy reading as energy waste.

---

## 🔍 Explainable Detection

Example:

> **AC Waste**

If an AC is running while the room has no occupants, WattWise can explain:

**"AC is running while the room has no occupants."**

It then recommends checking whether the AC can be switched off or controlled using occupancy-based or scheduled control.

This makes the system more understandable than a simple anomaly score.

---

## 🔮 What-If Simulator

The simulator allows users to change a hypothetical **waste-prevention rate** and see its potential effect.

It estimates:

- Potential energy saved
- Potential cost saved
- Remaining energy consumption

The prevention rate is a **prototype assumption**, not a guaranteed real-world saving.

---

## 📊 Current Prototype

The demonstration dataset contains:

- **20 rooms**
- **30 days**
- **24 hourly observations per day**
- **14,400 total records**

The current prototype produces:

- Energy consumption trends
- Potentially avoidable energy estimates
- Potentially avoidable cost estimates
- Waste-event detection
- Anomaly review events
- Room-level analysis
- What-If simulation
- WattWise Score

---

## 🏗️ System Architecture

```text
Simulated Smart-Meter Data
            ↓
      Data Processing
            ↓
 Energy + Occupancy + Weather
      + Device Context
            ↓
     Context Engine
            ↓
 ┌─────────────────────────┐
 │ Waste Detection         │
 │ Anomaly Detection       │
 └─────────────────────────┘
            ↓
    Explanation Engine
            ↓
 Recommendation Engine
            ↓
    What-If Simulator
            ↓
     Savings Dashboard
