import base64
import json
import os
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

PATIENTS_TABLE = os.environ["PATIENTS_TABLE"]
VITALS_TABLE = os.environ["VITALS_TABLE"]
ALERTS_TABLE = os.environ["ALERTS_TABLE"]
SNS_TOPIC_ARN = os.environ["SNS_ALERTS_TOPIC_ARN"]

patients_table = dynamodb.Table(PATIENTS_TABLE)
vitals_table = dynamodb.Table(VITALS_TABLE)
alerts_table = dynamodb.Table(ALERTS_TABLE)


def classify_risk(hr, spo2, bp_sys):
    if hr > 140 or spo2 < 88 or bp_sys > 180:
        return "critical"
    if hr > 120 or hr < 50 or spo2 < 92 or bp_sys > 160:
        return "warning"
    return "normal"


def lambda_handler(event, context):
    for record in event.get("Records", []):
        try:
            payload = base64.b64decode(record["kinesis"]["data"])
            data = json.loads(payload.decode("utf-8"))

            patient_id = data["patient_id"]
            hr = int(data["heart_rate"])
            spo2 = int(data["spo2"])
            bp_sys = int(data["bp_sys"])
            bp_dia = int(data["bp_dia"])
            timestamp = data.get("timestamp", datetime.now(timezone.utc).isoformat())

            # Determine anomaly
            risk = classify_risk(hr, spo2, bp_sys)
            is_anomaly = risk in ("warning", "critical")

            # 1) Insert into patient_vitals
            vitals_table.put_item(
                Item={
                    "patient_id": patient_id,
                    "timestamp": timestamp,
                    "heart_rate": hr,
                    "spo2": spo2,
                    "bp_sys": bp_sys,
                    "bp_dia": bp_dia,
                    "is_anomaly": is_anomaly,
                }
            )

            # 2) Update parent patient summary
            patients_table.update_item(
                Key={"patient_id": patient_id},
                UpdateExpression=(
                    "SET last_heart_rate=:hr, last_spo2=:spo2, "
                    "last_bp_sys=:bp_sys, last_bp_dia=:bp_dia, "
                    "last_vital_timestamp=:ts, risk_level=:risk"
                ),
                ExpressionAttributeValues={
                    ":hr": hr,
                    ":spo2": spo2,
                    ":bp_sys": bp_sys,
                    ":bp_dia": bp_dia,
                    ":ts": timestamp,
                    ":risk": risk,
                },
            )

            # 3) On anomaly → alerts table + SNS
            if is_anomaly:
                alert_id = f"{patient_id}-{timestamp}"
                message = (
                    f"Anomaly detected for patient {patient_id}:\n"
                    f"HR={hr}, SpO2={spo2}, BP={bp_sys}/{bp_dia}, Risk={risk}"
                )

                alerts_table.put_item(
                    Item={
                        "alert_id": alert_id,
                        "patient_id": patient_id,
                        "created_at": timestamp,
                        "message": message,
                        "level": risk,
                    }
                )

                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=f"[ALERT] Patient {patient_id} - {risk.upper()}",
                    Message=message,
                )

        except Exception as e:
            print("Error processing record:", e)

    return {"statusCode": 200, "body": "Processed batch"}