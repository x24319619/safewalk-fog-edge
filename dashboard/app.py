import os
from flask import Flask, render_template, jsonify
import boto3
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

def get_table():
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.environ.get("AWS_SESSION_TOKEN")
    )
    return dynamodb.Table(os.environ.get("TABLE_NAME", "safewalk_incidents"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/incidents")
def get_incidents():
    try:
        table = get_table()
        response = table.scan()
        incidents = response.get("Items", [])
        incidents.sort(
            key=lambda x: f"{x.get('date', '')} {x.get('timestamp', '')}",
            reverse=True
        )
        return jsonify({"incidents": incidents, "total": len(incidents)})
    except Exception as e:
        print(f" DynamoDB Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
def get_stats():
    try:
        table = get_table()
        today = datetime.now().strftime("%Y-%m-%d")
        response = table.scan()
        incidents = response.get("Items", [])
        today_incidents = [i for i in incidents if i.get("date") == today]
        critical = len([i for i in today_incidents if i.get("severity") == "CRITICAL"])
        warning  = len([i for i in today_incidents if i.get("severity") == "WARNING"])
        total    = len(today_incidents)
        return jsonify({
            "total"   : total,
            "critical": critical,
            "warning" : warning,
            "safe"    : total - critical - warning
        })
    except Exception as e:
        print(f" DynamoDB Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')