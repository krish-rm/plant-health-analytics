import os
import pandas as pd
import gcsfs
from airflow.models import Variable

# Load environment variables from Airflow Variables
RAW_CSV_PATH = Variable.get("RAW_CSV_PATH")
INGESTED_DATA_PATH = Variable.get("INGESTED_DATA_PATH")

def ingest_data():
    print(f"Reading raw CSV from: {RAW_CSV_PATH}")
    df = pd.read_csv(RAW_CSV_PATH)

    print(f"Saving ingested data to: {INGESTED_DATA_PATH}")
    fs = gcsfs.GCSFileSystem()
    with fs.open(INGESTED_DATA_PATH, 'w') as f:
        df.to_csv(f, index=False)

    print("✅ Ingestion completed.")

if __name__ == "__main__":
    ingest_data()
