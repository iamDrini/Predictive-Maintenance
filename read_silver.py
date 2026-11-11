import delta
from pyspark.sql import SparkSession

builder = SparkSession.builder \
    .appName("ReadSilverLayer") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
spark = delta.configure_spark_with_delta_pip(builder).getOrCreate()

df_silver = spark.read.format("delta").load("data/silver")

df_silver.printSchema()
df_silver.show(10, truncate=False)

spark.stop()