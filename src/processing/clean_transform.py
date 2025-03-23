import pandas as pd
import gcsfs
from airflow.models import Variable

# Load environment variables from Airflow Variables
INGESTED_DATA_PATH = Variable.get("INGESTED_DATA_PATH")  # GCS path
PROCESSED_DATA_PATH = Variable.get("PROCESSED_DATA_PATH")  # GCS path

def clean_data():
    print(f"Reading ingested raw data from: {INGESTED_DATA_PATH}")

    # Initialize GCSFS
    fs = gcsfs.GCSFileSystem()

    # Read CSV from GCS
    with fs.open(INGESTED_DATA_PATH, 'r') as f:
        df = pd.read_csv(f)

    # Convert Timestamp to datetime
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    print(f"Saving cleaned data to: {PROCESSED_DATA_PATH}")

    # Write Parquet to GCS
    with fs.open(PROCESSED_DATA_PATH, 'wb') as f:
        df.to_parquet(f, index=False)

    print("✅ Data cleaning completed.")

if __name__ == "__main__":
    clean_data()
