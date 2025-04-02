## 🚀 Deployment Guide for Plant Health Dashboard

The Plant Health Dashboard processes plant health environmental sensor data collected four times (morning, afternoon, evening, night) daily. This data is stored in **Google Cloud Storage (GCS)**, where it is ingested, cleaned, and transformed for weekly analysis (e.g., Week 46, 47, …), before being loaded into **BigQuery**. The **Airflow DAG** automates this batch processing, ensuring that the dashboard reflects up-to-date plant health insights.

---

### **Final Automated Workflow**
✅ **Airflow DAG** processes new sensor data (Week 46, 47, …), cleans it, and loads it into **BigQuery**.  
✅ **Dockerized App** fetches data from **BigQuery** and is deployed to **Cloud Run** for public access.  
✅ **Cloud Build** automates the build and redeployment process, ensuring seamless updates.

---

### 🔧 **Prerequisites**
Before deploying, ensure the following are set up:

- **Google Cloud SDK** installed and authenticated (`gcloud auth login`).
- **Google Cloud Project** (Example name: `plant-123456`) is active (`gcloud config set project plant-123456`).
- **Cloud Storage Bucket** (Example bucket: `gs://plant-bucket-123456`) created for raw and processed data.
- **BigQuery Dataset** exists to store processed data.
- **Cloud Composer (Airflow) environment** is set up for DAG execution.
- **Cloud Composer, Cloud Run, and Cloud Build APIs** are enabled:

  ```sh
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com composer.googleapis.com
  ```

---

### 📌 **Deployment Steps**

#### 1⃣ **Clone Repository**
To get started, clone the repository:

```bash
git clone https://github.com/krish-rm/plant-health-analytics.git
cd plant-health-analytics
```

#### 2⃣ **Upload Raw CSV to Google Cloud Storage (GCS)**

Before running the Airflow DAG, upload the raw CSV file to **Google Cloud Storage** (GCS):

1. **Ensure Google Cloud SDK is authenticated**:

   ```bash
   gcloud auth login
   gcloud config set project your-gcp-project-id
   ```

2. **Upload the raw CSV file**:

   ```bash
   gsutil cp data/raw/plant_health_data.csv gs://your-bucket-name/path/to/RAW_CSV_PATH/
   ```

   Replace:
   - `your-bucket-name` with the actual name of your GCS bucket.
   - `path/to/RAW_CSV_PATH/` with the path where the raw data file will be stored in GCS.

   For example:

   ```bash
   gsutil cp data/raw/plant_health_data.csv gs://plant-bucket-123456/raw_data/
   ```

   This will upload the raw CSV file to `gs://plant-bucket-123456/raw_data/plant_health_data.csv`.

---

#### 3⃣ **Set Up Cloud Composer (Airflow) Environment**

For first-time setup, create a Cloud Composer environment:

```bash
gcloud composer environments create plant-composer-env \
    --location us-central1 \
    --image-version composer-2-airflow-2 \
    --node-count 3 \
    --environment-size medium
```

Upload the **Airflow DAG**:

```bash
gsutil cp src/automation/airflow_dag.py gs://<BUCKET_NAME>/dags/
```

Also, upload the related scripts for the DAG (such as `ingest_pipeline.py`, `clean_transform.py`, and `move_to_bigquery.py`), as they will be used in the DAG tasks:

```bash
gsutil cp src/ingestion/ingest_pipeline.py gs://<BUCKET_NAME>/dags/
gsutil cp src/processing/clean_transform.py gs://<BUCKET_NAME>/dags/
gsutil cp src/processing/move_to_bigquery.py gs://<BUCKET_NAME>/dags/
```

Find the **Airflow UI URL**:

```bash
gcloud composer environments describe plant-composer-env \
    --location us-central1 --format="value(config.airflowUri)"
```

Access the **Airflow UI** by visiting the URL provided in the output of the above command.

---

#### 4⃣ **Set Airflow Variables**

Set the **Airflow variables** for the paths used in the ingestion process. These variables should point to the correct GCS locations:

1. **Set the `RAW_CSV_PATH` variable**:

   ```bash
   airflow variables set RAW_CSV_PATH "gs://plant-bucket-123456/raw_data/plant_health_data.csv"
   ```

2. **Set the `INGESTED_DATA_PATH` variable**:

   ```bash
   airflow variables set INGESTED_DATA_PATH "gs://plant-bucket-123456/processed_data/ingested_plant_health_data.csv"
   ```

These paths will be used by the **Airflow DAG** to read and store the data during the ingestion process.

---

#### 5⃣ **Execute Airflow DAG to Ingest, Clean, and Load Data to BigQuery**

Once your Airflow environment is set up, you can trigger the ETL process. The DAG ID is the identifier you gave to your Airflow DAG when defining it in your Python script. In the example provided, the DAG ID is `"plant_ai_pipeline"`:

```python
with DAG(
    "plant_ai_pipeline",  # This is the DAG ID
    default_args=default_args,
    schedule_interval=None,  # or any defined schedule
    catchup=False,
) as dag:
```

If you used the same ID (`"plant_ai_pipeline"`), you can run the following command to trigger the DAG and start the ETL process:

```bash
gcloud composer environments run plant-composer-env --location us-central1 dags trigger -- plant_ai_pipeline
```

**Important**:  
If you named your DAG differently in your script, make sure to replace `"plant_ai_pipeline"` with your DAG's actual name. For example, if your DAG ID is `"plant_health_etl"`, the command would be:

```bash
gcloud composer environments run plant-composer-env --location us-central1 dags trigger -- plant_health_etl
```

This command will trigger the ETL process, starting from data ingestion, followed by cleaning and transformation, and finally loading the data into **BigQuery**.

---

#### 6⃣ **Set Up IAM Permissions (One-Time Setup)**

Ensure the service account has the necessary permissions:

```bash
gcloud projects add-iam-policy-binding plant-123456 --member=serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com --role=roles/storage.admin && \
gcloud projects add-iam-policy-binding plant-123456 --member=serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com --role=roles/artifactregistry.writer && \
gcloud projects add-iam-policy-binding plant-123456 --member=serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com --role=roles/run.admin
```

---

#### 7⃣ **Trigger Cloud Build for Automated Deployment**

Navigate to the directory with the `plant-health-analytics` folder. Run **Cloud Build** to build the Docker image, push it, and deploy it to **Cloud Run** in one step:

```bash
gcloud builds submit --config cloud_build.yaml .
```

---

#### 8⃣ **Verify Cloud Run Deployment**

After deployment, check the **Cloud Run Service URL**:

```bash
gcloud run services describe plant-dashboard --region=us-central1 --format='value(status.url)'
```

or visit the URL displayed in the **Cloud Build** logs.

---

#### 9⃣ **Ensure Public Access to Cloud Run**

If Cloud Run is not accessible publicly, grant permissions:

```bash
gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker plant-health-dashboard
```

---

### ✅ **Deployment Complete!** 🚀

Your **Plant Health Dashboard** is now live at:

https://plant-health-dashboard-703716144022.us-central1.run.app/

And updates automatically with new sensor data!

