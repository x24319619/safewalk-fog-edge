import time
import random
import json
import paho.mqtt.client as mqtt

# ─── MQTT CONFIG (Fog Node Connection) ───────────────────────
BROKER = "localhost"
PORT   = 1883
TOPIC  = "campus/student/location"

# ─── STUDENT INFO ─────────────────────────────────────────────
STUDENT_ID   = "S001"
STUDENT_NAME = "Sonal"

# ─── MQTT SETUP ───────────────────────────────────────────────
client = mqtt.Client()
client.connect(BROKER, PORT)
print(" Sensor connected to Fog Node (MQTT Broker)")
print(" Sending sensor data every 5 seconds...\n")

# ─── SIMULATE SENSORS IN A LOOP ───────────────────────────────
while True:

    # Sensor 1 — GPS Speed (metres per second)
    speed = round(random.uniform(0.0, 2.5), 2)

    # Sensor 2 — Ambient Light (lux)
    light = round(random.uniform(0, 600), 1)

    # Sensor 3 — Stationary Timer (seconds stopped)
    stationary = random.choice([0, 0, 0, 30, 60, 90, 120])

    # Sensor 4 — Panic Button (mostly False)
    panic = random.choice([False, False, False, False, True])

    # Build the payload
    payload = {
        "student_id"     : STUDENT_ID,
        "student_name"   : STUDENT_NAME,
        "speed_ms"       : speed,
        "light_lux"      : light,
        "stationary_sec" : stationary,
        "panic"          : panic,
        "timestamp"      : time.strftime("%H:%M:%S")
    }

    # Convert to JSON and send to fog node
    message = json.dumps(payload)
    client.publish(TOPIC, message)

    # Print what was sent
    print(f"📤 Sent → {payload}")
    print("─" * 60)

    # Wait 5 seconds before next reading
    time.sleep(5)