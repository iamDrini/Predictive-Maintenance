import os
import delta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

BRONZE_DIR = "data/bronze"
SILVER_DIR = "data/silver"

# Spark Session mit Delta-Support starten
builder = SparkSession.builder \
    .appName("PredictiveMaintenanceETL")\
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = delta.configure_spark_with_delta_pip(builder).getOrCreate()

print("🚀 PySpark Session erfolgreich gestartet!")

# Sicherheitsprüfung & Einlesen der Bronze-Schicht
if not os.path.exists(BRONZE_DIR) or not os.listdir(BRONZE_DIR):
    print("❌ Keine Rohdaten in data/bronze gefunden!")
else:
    # Wichtig: multiLine=True fängt deine formatierten JSON-Dateien ab
    df_bronze = spark.read \
        .option("multiLine", "true") \
        .format("json") \
        .load(os.path.join(BRONZE_DIR, "*.json"))

    print("✅ Rohdaten erfolgreich eingelesen.")

    # Transformationen anwenden
    df_silver = df_bronze \
        .withColumn("timestamp", to_timestamp(col("timestamp"))) \
        .withColumn("temperature_celsius", col("temperature_celsius").cast("double")) \
        .withColumn("vibration_mms", col("vibration_mms").cast("double")) \
        .withColumn("rpm", col("rpm").cast("integer")) \
        .withColumn("simulated_anomaly", col("simulated_anomaly").cast("boolean"))

    df_silver = df_silver.orderBy("timestamp")

    # Als Delta-Tabelle in die Silver-Schicht schreiben
    df_silver.write \
        .format("delta") \
        .mode("overwrite") \
        .save(SILVER_DIR)

    print("🎉 Silver-Schicht erfolgreich als Delta-Tabelle gespeichert!")

    print("\n--- Daten-Vorschau (SILVER LAYER) ---")
    df_silver.show(10, truncate=False)

spark.stop()