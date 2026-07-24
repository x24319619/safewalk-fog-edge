import os
from flask import Flask, render_template, jsonify
import boto3
from dotenv import load_dotenv

# ─── LOAD AWS CREDENTIALS ─────────────────────────────────────
load_dotenv()

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# ─── AWS CONFIG ───────────────────────────────────────────────
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token     = os.getenv("AWS_SESSION_TOKEN")
)
table = dynamodb.Table("safewalk_incidents")


# ─── ROUTES ───────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/incidents")
def get_incidents():
    try:
        response = table.scan()
        incidents = response.get("Items", [])
        incidents.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return jsonify({"incidents": incidents, "total": len(incidents)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
def get_stats():
    try:
        response = table.scan()
        incidents = response.get("Items", [])
        critical = len([i for i in incidents if i.get("severity") == "CRITICAL"])
        warning  = len([i for i in incidents if i.get("severity") == "WARNING"])
        total    = len(incidents)
        return jsonify({
            "total"   : total,
            "critical": critical,
            "warning" : warning,
            "safe"    : total - critical - warning
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')