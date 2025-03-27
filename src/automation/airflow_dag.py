from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta

# Get the current date and set start_date to today
current_date = datetime.today()

# Load environment variables from Airflow Variables
GCS_BUCKET_NAME = Variable.get("GCS_BUCKET_NAME")
BQ_PROJECT_ID = Variable.get("GCP_PROJECT_ID")

# Define default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    'start_date': current_date,  # Start from the current date
    "retries": 1,
}

# Define DAG
with DAG(
    "plant_ai_pipeline",
    default_args=default_args,
    schedule_interval=None, # Set schedule_interval='@daily' for daily build
    catchup=False,
) as dag:
    
    ingest_task = BashOperator(
        task_id="ingest_data",
        bash_command="python /home/airflow/gcs/dags/ingest_pipeline.py",
    )
    
    clean_task = BashOperator(
        task_id="clean_data",
        bash_command="python /home/airflow/gcs/dags/clean_transform.py",
    )
    
    bq_task = BashOperator(
        task_id="load_to_bigquery",
        bash_command="python /home/airflow/gcs/dags/move_to_bigquery.py",
    )
    
    # Define task dependencies
    ingest_task >> clean_task >> bq_task
