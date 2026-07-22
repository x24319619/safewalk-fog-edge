import json
import paho.mqtt.client as mqtt

# ─── CONFIG ───────────────────────────────────────────────────
BROKER    = "localhost"
PORT      = 1883
SUB_TOPIC = "campus/student/location"   
PUB_TOPIC = "campus/alerts"             

# ─── RISK SCORING ENGINE (fog intelligence) ───────────────────
def compute_risk(data):
    score = 0

    # Factor 1 — Speed (max 30 points)
    if data["speed_ms"] < 0.2:
        score += 30
        print("     Speed critical — student not moving (+30)")
    elif data["speed_ms"] < 0.5:
        score += 15
        print("     Speed low — student barely moving (+15)")

    # Factor 2 — Stationary time (max 30 points)
    stop_score = min(data["stationary_sec"] / 10, 30)
    score += stop_score
    if stop_score > 0:
        print(f"    Stationary {data['stationary_sec']}s (+{stop_score})")

    # Factor 3 — Light level (max 20 points)
    if data["light_lux"] < 50:
        score += 20
        print("   ️  Very dark zone (+20)")
    elif data["light_lux"] < 150:
        score += 10
        print("   ️  Low light area (+10)")

    # Factor 4 — Panic button (immediate 100)
    if data["panic"]:
        score = 100
        print("    PANIC BUTTON PRESSED → Score = 100!")

    return round(score)

# ─── DECISION ENGINE ──────────────────────────────────────────
def make_decision(score, data, client):
    name = data["student_name"]

    if score >= 65:
        status = "CRITICAL"
        print(f"    CRITICAL — Alerting cloud for {name}!")
        alert = {
            "student_id"  : data["student_id"],
            "student_name": name,
            "risk_score"  : score,
            "severity"    : "CRITICAL",
            "timestamp"   : data["timestamp"],
            "message"     : f"Student {name} needs immediate help!"
        }
        client.publish(PUB_TOPIC, json.dumps(alert))

    elif score >= 35:
        status = "WARNING"
        print(f"   ⚡ WARNING — Monitoring {name} closely")
        alert = {
            "student_id"  : data["student_id"],
            "student_name": name,
            "risk_score"  : score,
            "severity"    : "WARNING",
            "timestamp"   : data["timestamp"],
            "message"     : f"Student {name} showing warning signs"
        }
        client.publish(PUB_TOPIC, json.dumps(alert))

    else:
        status = "SAFE"
        print(f"  SAFE — Score {score} is low. Not escalating to cloud.")

    return status

# ─── MQTT CALLBACKS ───────────────────────────────────────────
def on_connect(client, userdata, flags, reason_code, properties):
    print(" Fog Node connected to MQTT Broker")
    print(f" Listening for student data on: {SUB_TOPIC}\n")
    client.subscribe(SUB_TOPIC)

def on_message(client, userdata, msg):
    print("=" * 60)
    data = json.loads(msg.payload.decode())
    print(f" Received from {data['student_name']} at {data['timestamp']}")
    print(f"   Speed: {data['speed_ms']} m/s | "
          f"Light: {data['light_lux']} lux | "
          f"Stopped: {data['stationary_sec']}s | "
          f"Panic: {data['panic']}")
    print(f" Fog Node calculating risk score...")

    score = compute_risk(data)
    print(f"    Risk Score = {score}/100")

    make_decision(score, data, client)
    print("=" * 60 + "\n")

# ─── START FOG NODE ───────────────────────────────────────────
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)
print("  SafeWalk Fog Node starting...")
client.loop_forever()