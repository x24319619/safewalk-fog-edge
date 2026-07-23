import time
import random
import json
import yaml
import paho.mqtt.client as mqtt

# ─── LOAD CONFIG ──────────────────────────────────────────────
with open("sensors_config.yaml", "r") as f:
    config = yaml.safe_load(f)

BROKER       = config["mqtt"]["broker"]
PORT         = config["mqtt"]["port"]
TOPIC        = config["mqtt"]["topic"]
STUDENT_ID   = config["student"]["id"]
STUDENT_NAME = config["student"]["name"]
FREQUENCY    = config["sensors"]["frequency_seconds"]

# ─── MQTT SETUP ───────────────────────────────────────────────
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
print(f"✅ Sensor connected — Student: {STUDENT_NAME}")
print(f"📡 Sending every {FREQUENCY} seconds\n")

cycle = 0

while True:
    cycle += 1
    scenario = cycle % 3

    if scenario == 0:
        print(" Scenario: Normal Walk")
        cfg   = config["scenarios"]["normal"]
        speed = round(random.uniform(cfg["speed_min"], cfg["speed_max"]), 2)
        light = round(random.uniform(cfg["light_min"], cfg["light_max"]), 1)
        stationary = cfg["stationary"]
        panic      = cfg["panic"]

    elif scenario == 1:
        print(" Scenario: Stopped in Dark Zone")
        cfg   = config["scenarios"]["dark_zone"]
        speed = round(random.uniform(cfg["speed_min"], cfg["speed_max"]), 2)
        light = round(random.uniform(cfg["light_min"], cfg["light_max"]), 1)
        stationary = random.choice(cfg["stationary_options"])
        panic      = cfg["panic"]

    else:
        print(" Scenario: PANIC BUTTON!")
        cfg   = config["scenarios"]["panic"]
        speed = cfg["speed"]
        light = round(random.uniform(cfg["light_min"], cfg["light_max"]), 1)
        stationary = cfg["stationary"]
        panic      = cfg["panic"]

    payload = {
        "student_id"     : STUDENT_ID,
        "student_name"   : STUDENT_NAME,
        "speed_ms"       : speed,
        "light_lux"      : light,
        "stationary_sec" : stationary,
        "panic"          : panic,
        "timestamp"      : time.strftime("%H:%M:%S"),
    }

    client.publish(TOPIC, json.dumps(payload))
    print(f"📤 Sent: {payload}")
    print("-" * 60)

    time.sleep(FREQUENCY)