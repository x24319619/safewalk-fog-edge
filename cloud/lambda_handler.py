import json
import boto3
import os
from datetime import datetime

# ─── AWS SERVICES ─────────────────────────────────────────────
dynamodb = boto3.resource('dynamodb')
sns      = boto3.client('sns')

# ─── YOUR CONFIG (we will fill these after AWS setup) ─────────
TABLE_NAME = "safewalk_incidents"
SNS_TOPIC  = "arn:aws:sns:us-east-1:XXXX:safewalk-alerts"  # update later

# ─── MAIN LAMBDA HANDLER ──────────────────────────────────────
def handler(event, context):
    print("⚡ Lambda triggered!")
    print(f" Event received: {json.dumps(event)}")

    try:
        # ── Step 1: Parse the alert from fog node ──
        if isinstance(event.get('body'), str):
            alert = json.loads(event['body'])
        else:
            alert = event

        student_id   = alert.get('student_id',   'UNKNOWN')
        student_name = alert.get('student_name', 'UNKNOWN')
        risk_score   = alert.get('risk_score',   0)
        severity     = alert.get('severity',     'UNKNOWN')
        timestamp    = alert.get('timestamp',    datetime.now().strftime("%H:%M:%S"))
        message      = alert.get('message',      'No message')

        print(f" Processing alert for {student_name} — Score: {risk_score} — {severity}")

        # ── Step 2: Save to DynamoDB ──
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                'incident_id'  : f"{student_id}_{timestamp}",
                'student_id'   : student_id,
                'student_name' : student_name,
                'risk_score'   : str(risk_score),
                'severity'     : severity,
                'message'      : message,
                'timestamp'    : timestamp,
                'date'         : datetime.now().strftime("%Y-%m-%d")
            }
        )
        print(f" Incident saved to DynamoDB")

        # ── Step 3: Send SNS notification to security ──
        sns_message = f"""
 SafeWalk Campus Alert

Student  : {student_name} ({student_id})
Severity : {severity}
Risk Score: {risk_score}/100
Time     : {timestamp}
Message  : {message}

Please check on this student immediately.
        """

        sns.publish(
            TopicArn = SNS_TOPIC,
            Message  = sns_message,
            Subject  = f"SafeWalk {severity} Alert — {student_name}"
        )
        print(f" SNS notification sent to security!")

        # ── Step 4: Return success ──
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message'   : 'Alert processed successfully',
                'student'   : student_name,
                'severity'  : severity,
                'risk_score': risk_score
            })
        }

    except Exception as e:
        print(f" Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }