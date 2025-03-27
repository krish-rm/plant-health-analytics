from google.cloud import bigquery, storage
from google.cloud.exceptions import NotFound
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import os
import io


# Constants
BQ_PROJECT = "plant-454208"
BQ_DATASET = "plant_data"
BQ_TABLE = "plant_health"
GCS_BUCKET = "plant-ai-bucket-454208"
GCS_BLOB_NAME = "processed/cleaned_plant_health_data.parquet"
GCS_CORRECTED_BLOB_NAME = "processed/corrected_plant_health_data.parquet"
GCS_URI = f"gs://{GCS_BUCKET}/{GCS_BLOB_NAME}"
GCS_CORRECTED_URI = f"gs://{GCS_BUCKET}/{GCS_CORRECTED_BLOB_NAME}"

# Function to write DataFrame as Parquet directly to GCS
def write_parquet_to_gcs(df, bucket_name, destination_blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Convert DataFrame to Parquet in-memory
        table = pa.Table.from_pandas(df)
        parquet_buffer = io.BytesIO()
        pq.write_table(table, parquet_buffer)

        # Upload to GCS
        blob.upload_from_string(parquet_buffer.getvalue(), content_type="application/octet-stream")
        print(f"✅ Successfully uploaded Parquet to gs://{bucket_name}/{destination_blob_name}")
    
    except Exception as e:
        print(f"❌ Error writing Parquet to GCS: {e}")

# Function to process and load data to BigQuery
def load_parquet_to_bq():
    try:
        client = bigquery.Client()
        table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

        schema = [
            bigquery.SchemaField("Timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("Plant_ID", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("Soil_Moisture", "FLOAT"),
            bigquery.SchemaField("Ambient_Temperature", "FLOAT"),
            bigquery.SchemaField("Soil_Temperature", "FLOAT"),
            bigquery.SchemaField("Humidity", "FLOAT"),
            bigquery.SchemaField("Light_Intensity", "FLOAT"),
            bigquery.SchemaField("Soil_pH", "FLOAT"),
            bigquery.SchemaField("Nitrogen_Level", "FLOAT"),
            bigquery.SchemaField("Phosphorus_Level", "FLOAT"),
            bigquery.SchemaField("Potassium_Level", "FLOAT"),
            bigquery.SchemaField("Chlorophyll_Content", "FLOAT"),
            bigquery.SchemaField("Electrochemical_Signal", "FLOAT"),
            bigquery.SchemaField("Plant_Health_Status", "STRING"),
        ]

        # Check if table exists, else create it
        try:
            client.get_table(table_id)
            print(f"✅ Table {table_id} already exists.")
        except NotFound:
            table = bigquery.Table(table_id, schema=schema)
            table.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field="Timestamp") 
            client.create_table(table)
            print(f"✅ Created partitioned table {table_id}.") # Created a table partitioned by Timestamp (DAY)

        # Read Parquet file from GCS and fix timestamp
        print(f"📥 Reading Parquet from GCS: {GCS_URI}...")
        df = pd.read_parquet(GCS_URI)

        if df.empty:
            print("⚠️ Warning: Read Parquet file is empty!")

        print("🛠️ Fixing timestamp column...")

        # Convert Timestamp column and handle invalid values
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

        # Ensure timestamps are within valid range
        min_date, max_date = pd.Timestamp("2000-01-01"), pd.Timestamp("2100-12-31")
        df = df[(df["Timestamp"] >= min_date) & (df["Timestamp"] <= max_date)]

        # Drop rows with invalid timestamps
        df = df.dropna(subset=["Timestamp"])

        # Convert timestamps to microseconds precision
        df["Timestamp"] = df["Timestamp"].astype("datetime64[us]")

        # Save corrected Parquet to new file instead of overwriting
        write_parquet_to_gcs(df, GCS_BUCKET, GCS_CORRECTED_BLOB_NAME)

        # Load corrected file from GCS to BigQuery
        print(f"📊 Loading corrected Parquet into BigQuery table: {table_id}...")
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        load_job = client.load_table_from_uri(GCS_CORRECTED_URI, table_id, job_config=job_config)
        load_job.result()  # Wait for job to complete

        print(f"🚀 Data successfully loaded into {table_id}")
    
    except Exception as e:
        print(f"❌ Error in load_parquet_to_bq: {e}")

# Run the function
if __name__ == "__main__":
    load_parquet_to_bq()
