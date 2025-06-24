# Weather-Monitoring-System-using-IOT
## ⚙️ Features:

- 🌡️ Temperature & Humidity monitoring (DHT11)
- ⛅ Atmospheric pressure monitoring (BME280)
- 📬 Email alerts using AWS SES when thresholds are exceeded
- 🧠 Sensor calibration and retry logic
- 🔁 Background threading for continuous monitoring

---

## 📌 Prerequisites:

- Raspberry Pi (GPIO enabled)
- Python 3.7+
- DHT11 and BME280 sensors
- AWS Account (IAM, IoT Core, SES)

---

## 🔧 Installation:

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/Email_Alert_IoT_Project.git
cd Email_Alert_IoT_Project
```
2. ** Install dependencies **
```bash
pip install -r requirements.txt
```
3. ** Run the Script**
```bash
python3 Richu_Final_Working_Email.py
```
---
## 🔐 AWS Setup:

  Configure your AWS IoT Core with a device, policy, and certificates.
  
  Update MQTT client section in the script:
  
  Endpoint
  
  Root CA
  
  Certificate & Private key
  
  Ensure your IAM role has permissions for iot:Publish and SES for email.
---
## 📫 Email Alerts:

Alerts are sent if any of the following conditions are met:

    Temperature > 30°C

    Humidity > 80%

    Pressure < 900 hPa

You can customize these thresholds in the script.
---
## 🧪 Sensor Calibration:

The script includes a 10-second warm-up and calibration loop for more reliable DHT11 readings.
---



