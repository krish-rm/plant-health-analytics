from google.cloud import bigquery, storage
from google.api_core.exceptions import NotFound
from airflow.models import Variable

# Load environment variables from Airflow Variables
BQ_PROJECT = Variable.get("GCP_PROJECT_ID")
BQ_DATASET = Variable.get("BQ_DATASET")
BQ_TABLE = Variable.get("BQ_TABLE")
GCS_BUCKET_NAME = Variable.get("GCS_BUCKET_NAME")
GCS_PROCESSED_DESTINATION_BLOB = Variable.get("GCS_PROCESSED_DESTINATION_BLOB")
PROCESSED_DATA_PATH = Variable.get("PROCESSED_DATA_PATH")

# def upload_to_gcs():
#     """Uploads processed data to GCS."""
#     print(f"Uploading {PROCESSED_DATA_PATH} to GCS...")
#     client = storage.Client()
#     bucket = client.bucket(GCS_BUCKET_NAME)
#     blob = bucket.blob(GCS_PROCESSED_DESTINATION_BLOB)
#     blob.upload_from_filename(PROCESSED_DATA_PATH)
    
#     gcs_uri = f"gs://{GCS_BUCKET_NAME}/{GCS_PROCESSED_DESTINATION_BLOB}"
#     print(f"✅ Uploaded to {gcs_uri}")
#     return gcs_uri

def create_dataset_if_not_exists(client):
    """Creates BigQuery dataset if it doesn't exist."""
    dataset_id = f"{BQ_PROJECT}.{BQ_DATASET}"
    
    try:
        client.get_dataset(dataset_id)  # Check if dataset exists
        print(f"✅ Dataset {dataset_id} already exists.")
    except NotFound:  # Only create dataset if it doesn't exist
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"  # Adjust location as needed
        client.create_dataset(dataset, timeout=30)
        print(f"✅ Created dataset {dataset_id} in US.")

def load_parquet_to_bq():
    """Loads Parquet data from GCS to BigQuery."""
    client = bigquery.Client(project=BQ_PROJECT)

    # Ensure dataset exists before loading data
    create_dataset_if_not_exists(client)

    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
    # gcs_uri = upload_to_gcs()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE  # Overwrites the table
    )

    print(f"Loading data from {PROCESSED_DATA_PATH} into {table_id}...")
    load_job = client.load_table_from_uri(PROCESSED_DATA_PATH, table_id, job_config=job_config)
    load_job.result()  # Wait for the job to complete

    print(f"✅ Data successfully loaded into {table_id}")

if __name__ == "__main__":
    load_parquet_to_bq()
