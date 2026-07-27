import time
import random
import json
from pathlib import Path
import yaml
import paho.mqtt.client as mqtt

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR.parent / "sensors_config.yaml"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"Could not find config file at {CONFIG_PATH}")

with CONFIG_PATH.open("r") as f:
    config = yaml.safe_load(f)

BROKER       = config["mqtt"]["broker"]
PORT         = config["mqtt"]["port"]
TOPIC        = config["mqtt"]["topic"]
STUDENT_ID   = config["student"]["id"]
STUDENT_NAME = config["student"]["name"]
FREQUENCY_SECONDS = config.get("sensors", {}).get("frequency_seconds", 5)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
print(f" Sensor connected — Student: {STUDENT_NAME}")

# ─── NCI Campus Locations ──────────────────────────────
LOCATIONS = [
    {"name": "Main Library",      "lat": 53.3498, "lng": -6.2603},
    {"name": "Student Car Park",  "lat": 53.3495, "lng": -6.2610},
    {"name": "Back Gate",         "lat": 53.3502, "lng": -6.2615},
    {"name": "Sports Centre",     "lat": 53.3490, "lng": -6.2598},
    {"name": "Accommodation",     "lat": 53.3505, "lng": -6.2620},
]

cycle = 0

while True:
    cycle += 1
    scenario = cycle % 10
    location = random.choice(LOCATIONS)

    if scenario in [0, 1, 2, 3, 4, 5, 6]:
        print(" Scenario: Normal Walk")
        speed      = round(random.uniform(1.0, 2.5), 2)
        light      = round(random.uniform(200, 600), 1)
        stationary = 0
        panic      = False

    elif scenario in [7, 8]:
        print(" Scenario: Stopped in Dark Zone")
        speed      = round(random.uniform(0.0, 0.1), 2)
        light      = round(random.uniform(10, 45), 1)
        stationary = random.choice([120, 150])
        panic      = False

    else:
        print(" Scenario: PANIC BUTTON!")
        speed      = 0.0
        light      = round(random.uniform(5, 30), 1)
        stationary = 200
        panic      = True

    payload = {
        "student_id"     : STUDENT_ID,
        "student_name"   : STUDENT_NAME,
        "speed_ms"       : speed,
        "light_lux"      : light,
        "stationary_sec" : stationary,
        "panic"          : panic,
        "location"       : location["name"],
        "lat"            : location["lat"],
        "lng"            : location["lng"],
        "timestamp"      : time.strftime("%H:%M:%S"),
        "date"           : time.strftime("%Y-%m-%d"),
    }

    client.publish(TOPIC, json.dumps(payload))
    print(f" Sent: {payload}")
    print("-" * 60)
    time.sleep(FREQUENCY_SECONDS)
