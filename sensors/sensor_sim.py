import time
import random
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "campus/student/location"

STUDENT_ID = "S001"
STUDENT_NAME = "Sonal"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
print("Sensor connected to Fog Node")
print("Sending sensor data every 5 seconds\n")

cycle = 0

while True:
    cycle += 1
    scenario = cycle % 3

    if scenario == 0:
        print("Scenario: Normal Walk")
        speed = round(random.uniform(1.0, 2.5), 2)
        light = round(random.uniform(200, 600), 1)
        stationary = 0
        panic = False

    elif scenario == 1:
        print("Scenario: Stopped in Dark Zone")
        speed = round(random.uniform(0.0, 0.1), 2)
        light = round(random.uniform(10, 45), 1)
        stationary = random.choice([120, 150, 180, 200])
        panic = False

    else:
        print("Scenario: PANIC BUTTON!")
        speed = 0.0
        light = round(random.uniform(5, 30), 1)
        stationary = 200
        panic = True

    payload = {
        "student_id": STUDENT_ID,
        "student_name": STUDENT_NAME,
        "speed_ms": speed,
        "light_lux": light,
        "stationary_sec": stationary,
        "panic": panic,
        "timestamp": time.strftime("%H:%M:%S"),
    }

    message = json.dumps(payload)
    client.publish(TOPIC, message)
    print(f"Sent: {payload}")
    print("-" * 60)

    time.sleep(5)
