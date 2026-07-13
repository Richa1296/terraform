from pyspark.sql import SparkSession

# Initialize Spark with Apache Iceberg configurations
spark = SparkSession.builder \
    .appName("CreateIcebergTable") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.dev", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.dev.type", "hadoop") \
    .config("spark.sql.catalog.dev.warehouse", "gs://payments-dev-iceberg-data/warehouse") \
    .getOrCreate()

# 1. Create a sample DataFrame
data = [
    (1, "United States", "USD"),
    (2, "Singapore", "SGD"),
    (3, "Japan", "JPY"),
    (4, "United Kingdom", "GBP")
]
columns = ["country_id", "country_name", "currency"]
df = spark.createDataFrame(data, columns)

# 2. Write the DataFrame as an Apache Iceberg table
df.write \
    .format("iceberg") \
    .mode("overwrite") \
    .save("dev.db.countries")

print("Apache Iceberg table successfully created in GCS!")
