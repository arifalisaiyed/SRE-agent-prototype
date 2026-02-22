import json
import time
import random
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

print("🚀 Starting SRE Simulator (Producer)...")

boot_server = os.getenv('KAFKA_BOOTSTRAP_SERVER')
user = os.getenv('KAFKA_USERNAME')
pwd = os.getenv('KAFKA_PASSWORD')

print(f"DEBUG: Bootstrap Server found: {'YES' if boot_server else 'NO'}")
print(f"DEBUG: Username found: {'YES' if user else 'NO'}")

if not boot_server or not user or not pwd:
    print("❌ CRITICAL ERROR: One or more .env variables are MISSING!")
    print("Please ensure your .env file is in the same folder as this script.")
    exit()

try:
    producer = KafkaProducer(
        bootstrap_servers=boot_server,
        security_protocol="SASL_PLAINTEXT",
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=user,
        sasl_plain_password=pwd,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=10000
    )
    print("✅ SUCCESS: Connected to Kafka Cluster!")
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
    exit()

servers = ["web-server-01", "db-server-02", "cache-node-03"]
errors = ["OOM Exception", "High CPU Usage", "Disk Partition Full"]

print("📤 Sending logs every 5 seconds... Press Ctrl+C to stop.")

try:
    while True:
        log_entry = {
            "server_id": random.choice(servers),
            "error_type": random.choice(errors),
            "severity": "CRITICAL",
            "timestamp": time.ctime()
        }
        producer.send('system-alerts', log_entry)
        print(f"Sent: {log_entry['error_type']} from {log_entry['server_id']}")
        time.sleep(60)
except KeyboardInterrupt:
    print("\nStopping Producer...")
finally:
    producer.close()