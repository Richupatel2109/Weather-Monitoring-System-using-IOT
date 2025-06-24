import sys
sys.path.insert(0, "/home/richupatel/myenv/lib/python3.11/site-packages")

import time
import json
import threading
import RPi.GPIO as GPIO
import dht11
import board
import busio
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient                                                           
TEMP_THRESHOLD = 30
HUMIDITY_THRESHOLD = 80
PRESSURE_THRESHOLD = 900
ALERT_INTERVAL_SECONDS = 120
should_continue = False
sensor_thread = None


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
sensor = dht11.DHT11(pin=17)

print("Warming up DHT22 sensor...")
time.sleep(10)

print("Calibrating...")
for _ in range(10):
    sensor.read()
    time.sleep(1)
print("DHT22 Ready.\n")

def get_valid_read(retries=7, delay=2):
    for _ in range(retries):
        result = sensor.read()
        if result.is_valid():
            return result
        time.sleep(delay)
    return None

i2c = busio.I2C(board.SCL, board.SDA)
try:
    from adafruit_bme280 import basic as bme_module
    bme_sensor = bme_module.Adafruit_BME280_I2C(i2c, address=0x76)
    bme_sensor.sea_level_pressure = 1013.25
    print("BME280 initialized.\n")
except Exception as e:
    print(f"Error initializing BME280: {e}")
    bme_sensor = None

client = AWSIoTMQTTClient("MyIotThing")
client.configureEndpoint("a13k1q0bxoum1d-ats.iot.us-east-2.amazonaws.com", 8883)
client.configureCredentials(
    "/home/richupatel/Desktop/final proj richu/Amazon-root-CA-1.pem",
    "/home/richupatel/Desktop/final proj richu/private.pem.key",
    "/home/richupatel/Desktop/final proj richu/device.pem.crt"
)
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)

def sensor_loop():
    global should_continue
    last_alert_time = 0  

    while should_continue:
        dht_result = get_valid_read()
        if dht_result and bme_sensor:
            temperature = dht_result.temperature
            humidity = dht_result.humidity
            pressure = round(bme_sensor.pressure, 1)

            payload = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure
            }

            print("Publishing sensor data:\n", json.dumps(payload, indent=2))
            client.publish("myiot/sensor/data", json.dumps(payload), 1)

            if (temperature > TEMP_THRESHOLD or
                humidity > HUMIDITY_THRESHOLD or
                pressure > PRESSURE_THRESHOLD):

                current_time = time.time()
                if current_time - last_alert_time >= ALERT_INTERVAL_SECONDS:
                    print("Threshold exceeded! Sending critical alert...")
                    client.publish("myiot/sensor/critical", json.dumps(payload), 1)
                    last_alert_time = current_time
                else:
                    print("Alert throttled. Waiting for 2-minute interval.")
        else:
            print("Sensor read failed.\n")

        time.sleep(10)


def custom_callback(client, userdata, message):
    global should_continue, sensor_thread
    try:
        command = json.loads(message.payload.decode())
        if command.get("action") == "start_reading":
            if not should_continue:
                print("Received 'start_reading' command")
                should_continue = True
                sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
                sensor_thread.start()
        elif command.get("action") == "stop_reading":
            print("Received 'stop_reading' command")
            should_continue = False
    except Exception as e:
        print(f"Command error: {e}")

client.connect()
print("Connected to AWS IoT Core")
client.subscribe("myiot/sensor/data", 1, custom_callback)
print("Subscribed to: myiot/sensor/data\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up. Exiting.")
      