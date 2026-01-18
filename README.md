# 🌦️ WeatherBox – Real-Time Weather Prediction System

## Overview

**WeatherBox** is a real-time, sensor-driven weather monitoring and prediction system designed to collect live environmental data and generate short-term weather forecasts using a hybrid machine learning and deep learning pipeline. The system integrates embedded hardware sensors, Wi-Fi–based data transmission, a local backend server, and a Flask-based web application to visualize both real-time and predicted weather parameters.

Unlike traditional weather applications that rely on third-party APIs or satellite datasets, WeatherBox operates on **direct, localized sensor data**, making it highly effective for micro-climate monitoring, edge-based analytics, and experimental meteorology.

---

## System Architecture

WeatherBox follows a modular, layered architecture composed of four primary components:

1. Sensor Hardware Layer  
2. Data Ingestion & Communication Layer  
3. Prediction & Processing Layer  
4. Visualization & Web Interface Layer  

Each layer is loosely coupled to support scalability, maintainability, and future extensions such as cloud deployment or distributed sensor networks.

---

## 1. Sensor Hardware Layer

The WeatherBox device is equipped with multiple environmental sensors that continuously monitor localized atmospheric conditions. Typical sensors include:

- Temperature Sensor – Real-time ambient temperature measurement  
- Humidity Sensor – Relative humidity monitoring  
- Wind Speed Sensor – Airflow velocity detection  
- Optional Sensors – Atmospheric pressure, rainfall, light intensity  

All sensors are interfaced with a Wi-Fi–enabled microcontroller (e.g., ESP32 / ESP8266), which performs data acquisition, preliminary validation, and wireless transmission.

Sensor readings are sampled at fixed intervals to maintain temporal consistency and minimize signal noise.

---

## 2. Data Ingestion & Communication Layer

Sensor data is transmitted via **Wi-Fi** to a **local backend server**, ensuring low latency and independence from cloud connectivity. Each transmitted payload includes:

- Timestamped sensor readings  
- Sensor identifiers  
- Normalized and unit-consistent values  

The backend validates incoming data, handles missing or corrupted readings, and queues the data for processing and prediction.

---

## 3. Prediction & Processing Layer

The WeatherBox prediction engine is responsible for transforming real-time sensor data into short-term weather forecasts using a **hybrid modeling approach**.

### Data Preprocessing

Before model inference, the data undergoes multiple preprocessing steps:

- Missing value imputation  
- Noise filtering and smoothing  
- Feature scaling and normalization  
- Time-series windowing and sequence generation  

These steps ensure compatibility across both traditional machine learning and deep learning models.

---

## Models Used

WeatherBox employs **multiple specialized models**, each optimized for specific prediction tasks.

### RandomForestClassifier

The **RandomForestClassifier** is used for **weather-type classification**, leveraging its robustness and ability to handle nonlinear relationships.

**Purpose:**
- Classifies weather conditions such as Clear, Cloudy, Rainy, Windy, etc.

**Input Features:**
- Temperature  
- Humidity  
- Wind Speed  
- Derived statistical features  

**Why Random Forest?**
- High interpretability  
- Resistant to overfitting  
- Performs well on structured sensor data  

---

### GRU-Based Recurrent Neural Network (RNN)

A **Gated Recurrent Unit (GRU) RNN** is employed for **time-series forecasting** of continuous weather parameters.

**Purpose:**
- Predicts future values for:
  - Temperature  
  - Humidity  
  - Wind Speed  

**Forecast Horizon:**
- Next 10 hours from the current time  

**Why GRU?**
- Efficient learning of temporal dependencies  
- Lower computational cost compared to LSTM  
- Well-suited for real-time prediction systems  

The GRU model processes sliding windows of historical sensor data to capture short-term atmospheric dynamics.

---

### Hybrid Prediction Strategy

- GRU RNN → Predicts continuous numerical parameters  
- RandomForestClassifier → Determines categorical weather type  

This hybrid approach improves prediction accuracy while keeping inference latency low.

---

## 4. Visualization & Web Interface Layer

WeatherBox uses a **Flask-based web application** to display real-time sensor values and predicted forecasts.

### Flask Backend

The Flask server provides:

- REST APIs for live sensor data  
- Prediction endpoints for model outputs  
- Model inference orchestration  

### Frontend Dashboard

The web dashboard displays:

- Live environmental readings  
- Hourly forecasts for the next 10 hours  
- Weather-type classification results  
- Trend graphs for temperature, humidity, and wind speed  

The interface is lightweight, responsive, and optimized for local network deployment.

---

## Data Flow Summary

1. Sensors capture real-time environmental data  
2. Data is transmitted via Wi-Fi to the local server  
3. Backend preprocesses and validates sensor inputs  
4. GRU RNN predicts future weather parameters  
5. RandomForestClassifier classifies weather type  
6. Flask app visualizes real-time and predicted data  

---

## Key Features

- Real-time sensor-based data acquisition  
- Wi-Fi–enabled local server communication  
- Hybrid ML + Deep Learning prediction pipeline  
- 10-hour short-term weather forecasting  
- Interactive Flask-based visualization  
- Modular and extensible system design  

---

## Future Enhancements

- Cloud-based deployment and remote monitoring  
- Distributed WeatherBox sensor networks  
- Advanced deep learning architectures (LSTM, Transformers)  
- Model retraining pipelines with continuous learning  
- Mobile and cross-platform application support  

---

## Use Cases

- Localized weather monitoring  
- Smart agriculture and greenhouse systems  
- Environmental research and experimentation  
- IoT and edge-AI projects  
- Educational demonstrations of ML & time-series forecasting  

---

## Conclusion

WeatherBox showcases the practical integration of **IoT hardware, real-time data streaming, machine learning classification, deep learning–based time-series forecasting, and web visualization**. By utilizing **RandomForestClassifier** and **GRU RNN models**, the system delivers accurate, low-latency, and localized weather predictions without reliance on third-party APIs.

This project serves as a scalable foundation for intelligent weather monitoring systems and highlights real-world applications of hybrid AI pipelines in IoT environments.
