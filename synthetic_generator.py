import json
import random
import time
from datetime import datetime, timezone

import boto3

# ------------ CONFIG ------------

AWS_REGION = "us-east-1"
KINESIS_STREAM_NAME = "patient-vitals-stream"
SYSTEM_CONFIG_TABLE = "system_config"

# Seconds to sleep when stream is OFF
SLEEP_WHEN_OFF = 5

# Base interval between readings per patient (will jitter)
BASE_INTERVAL_SECONDS = 5

# ------------ AWS CLIENTS ------------

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
config_table = dynamodb.Table(SYSTEM_CONFIG_TABLE)

kinesis = boto3.client("kinesis", region_name=AWS_REGION)

# ------------ PATIENTS ------------

PATIENTS = [
    {"patient_id": "p1", "name": "Alice Johnson"},
    {"patient_id": "p2", "name": "Bob Smith"},
    {"patient_id": "p3", "name": "Carlos Diaz"},
    {"patient_id": "p4", "name": "Diana Patel"},
]

# ------------ VITAL GENERATION LOGIC ------------


def generate_normal_vitals():
    """Return a normal-ish set of vitals."""
    heart_rate = random.randint(65, 95)      # bpm
    spo2 = random.randint(95, 99)            # %
    bp_sys = random.randint(110, 130)        # mmHg
    bp_dia = random.randint(70, 85)          # mmHg
    return heart_rate, spo2, bp_sys, bp_dia


def generate_anomaly_vitals():
    """Return an anomalous set of vitals."""
    # Pick a random anomaly type
    anomaly_type = random.choice(["tachy", "brady", "hypoxia", "hypertension"])

    if anomaly_type == "tachy":
        heart_rate = random.randint(130, 160)
        spo2 = random.randint(90, 96)
        bp_sys = random.randint(130, 170)
        bp_dia = random.randint(80, 100)
    elif anomaly_type == "brady":
        heart_rate = random.randint(35, 50)
        spo2 = random.randint(92, 98)
        bp_sys = random.randint(100, 120)
        bp_dia = random.randint(60, 80)
    elif anomaly_type == "hypoxia":
        heart_rate = random.randint(90, 130)
        spo2 = random.randint(80, 91)
        bp_sys = random.randint(110, 140)
        bp_dia = random.randint(70, 90)
    else:  # hypertension
        heart_rate = random.randint(80, 110)
        spo2 = random.randint(94, 99)
        bp_sys = random.randint(165, 190)
        bp_dia = random.randint(90, 110)

    return heart_rate, spo2, bp_sys, bp_dia


def get_stream_status():
    """Read stream_status from system_config table (ON / OFF)."""
    try:
        resp = config_table.get_item(Key={"key": "stream_status"})
        item = resp.get("Item")
        if not item:
            return "OFF"
        return item.get("value", "OFF")
    except Exception as e:
        print(f"[CONFIG] Error reading stream_status: {e}")
        return "OFF"


def send_vital_to_kinesis(patient_id, heart_rate, spo2, bp_sys, bp_dia):
    """Send one reading to Kinesis."""
    payload = {
        "patient_id": patient_id,
        "heart_rate": heart_rate,
        "spo2": spo2,
        "bp_sys": bp_sys,
        "bp_dia": bp_dia,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    data_str = json.dumps(payload)
    kinesis.put_record(
        StreamName=KINESIS_STREAM_NAME,
        PartitionKey=patient_id,
        Data=data_str.encode("utf-8"),  # boto3 will base64 it for Kinesis
    )

    print(
        f"[KINESIS] Sent for {patient_id}: "
        f"HR={heart_rate}, SpO2={spo2}, BP={bp_sys}/{bp_dia}"
    )


def main():
    print("Starting synthetic data generator...")
    print(f"Region: {AWS_REGION}, Stream: {KINESIS_STREAM_NAME}")
    print(f"System config table: {SYSTEM_CONFIG_TABLE}")
    print(f"Patients: {[p['patient_id'] for p in PATIENTS]}")

    while True:
        status = get_stream_status()
        if status != "ON":
            print(f"[STATUS] stream_status is {status}. Sleeping {SLEEP_WHEN_OFF}s...")
            time.sleep(SLEEP_WHEN_OFF)
            continue

        # stream_status == ON -> generate readings for each patient
        for patient in PATIENTS:
            patient_id = patient["patient_id"]

            # 10–20% chance of anomaly, otherwise normal
            if random.random() < 0.15:
                hr, spo2, bp_sys, bp_dia = generate_anomaly_vitals()
                print(f"[GEN] Anomaly for {patient_id}")
            else:
                hr, spo2, bp_sys, bp_dia = generate_normal_vitals()
                print(f"[GEN] Normal for {patient_id}")

            try:
                send_vital_to_kinesis(patient_id, hr, spo2, bp_sys, bp_dia)
            except Exception as e:
                print(f"[ERROR] Failed to send for {patient_id}: {e}")

            # small per-patient delay to spread out events
            time.sleep(random.uniform(0.5, 1.5))

        # Wait a bit between overall cycles
        cycle_sleep = BASE_INTERVAL_SECONDS + random.uniform(-2, 3)
        cycle_sleep = max(1, cycle_sleep)
        print(f"[LOOP] Completed one cycle. Sleeping {cycle_sleep:.1f}s...\n")
        time.sleep(cycle_sleep)


if __name__ == "__main__":
    main()