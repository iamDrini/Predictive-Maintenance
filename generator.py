import json
import math
import os
import random
import time
from datetime import datetime

# Ordnerstruktur für das lokale Lakehouse (Bronze-Schicht) erstellen
OUTPUT_DIR = os.path.join("data", "bronze")
os.makedirs(OUTPUT_DIR, exist_ok=True)

step = 0

try:
    while True:
        step += 1
        timestamp = datetime.now().isoformat()
        
        # Normale Betriebsparameter (Basis-Sinuskurve mit leichtem Rauschen)
        base_temp = 65.0 + math.sin(step / 10.0) * 2.0 + random.uniform(-0.5, 0.5)
        base_vibration = 2.1 + math.cos(step / 5.0) * 0.3 + random.uniform(-0.1, 0.1)
        base_rpm = 1500 + random.randint(-15, 15)
        
        is_anomaly_injected = False

        # Ab Schritt 30 simulieren wir einen schleichenden Lagerschaden
        if step > 30:
            anomaly_factor = (step - 30) * 0.15
            base_vibration += anomaly_factor + random.uniform(0.1, 0.4)
            base_temp += anomaly_factor * 0.5
            base_rpm -= int(anomaly_factor * 10)
            is_anomaly_injected = True
            print(f"⚠️ [STEP {step}] SIMULIERTER VERSCHLEISS: Vibration = {base_vibration:.2f} mm/s")
        else:
            print(f"🟢 [STEP {step}] Normalbetrieb: Vibration = {base_vibration:.2f} mm/s")

        # Datensatz aufbauen
        record = {
            "sensor_id": "MOTOR_BEARING_01",
            "timestamp": timestamp,
            "temperature_celsius": round(base_temp, 2),
            "vibration_mms": round(base_vibration, 2),
            "rpm": base_rpm,
            "simulated_anomaly": is_anomaly_injected
        }

        # Als einzelne JSON-Datei abspeichern (simuliert eingehende Streaming-Events)
        filename = f"sensor_readings_{int(time.time())}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w") as f:
            json.dump(record, f, indent=2)

        time.sleep(2)  # Alle 2 Sekunden ein neues Event

except KeyboardInterrupt:
    print("\n🛑 Generator gestoppt.")