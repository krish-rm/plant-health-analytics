# 🚀 Deployment Guide for Plant Health Dashboard

The Plant Health Dashboard processes plant health environmental sensor data collected four times (morning, afternoon, evening, night) daily. This data is stored in **Google Cloud Storage (GCS)**, where it is ingested, cleaned, and transformed for weekly analysis (e.g., Week 46, 47, …), before being loaded into **BigQuery**. The **Airflow DAG** automates this batch processing, ensuring that the dashboard reflects up-to-date plant health insights.


## Final Automated Workflow
✅ **Airflow DAG** processes new sensor data (Week 46, 47, …),
   cleans it, and loads it into **BigQuery**.  
✅ **Dockerized App** fetches data from **BigQuery**
   and is deployed to **Cloud Run** for public access.  
✅ **Cloud Build** automates the build and redeployment process,
   ensuring seamless updates.

---

## 🔧 Prerequisites  
Before deploying, ensure the following are set up:  

- **Google Cloud SDK** installed and authenticated (`gcloud auth login`).  
- **Google Cloud Project** (`plant-123456`) is active (`gcloud config set project plant-123456`).  
- **Cloud Storage Bucket** (`gs://plant-bucket-123456`) created for raw and processed data.  
- **BigQuery Dataset** exists to store processed data.  
- **Cloud Composer (Airflow) environment** is set up for DAG execution.  
- **Cloud Composer, Cloud Run and Cloud Build APIs** are enabled:  

  ```sh
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com composer.googleapis.com
  ```  
- **(Optional) Terraform for Automated Provisioning**
Instead of manually creating GCP resources, Terraform can automate this:

  ```sh
   cd terraform
   terraform init
   terraform apply -auto-approve
  ``` 

## Choose from day, week, month for analysis, partition accordingly and apply transformation for optimization and cost effectiveness

### 1️⃣ Partitioning BigQuery Table

- Partition by `DATE(timestamp_column)` for daily partitions. (CURRENT IMPLEMENTATION)

- Use weekly partitions by extracting the ISO week:

```sql
CREATE OR REPLACE TABLE `your_project.your_dataset.your_table`
PARTITION BY TIMESTAMP_TRUNC(timestamp_column, WEEK)
AS SELECT * FROM `your_project.your_dataset.source_table`;
```

- For monthly partitions:

```sql
CREATE OR REPLACE TABLE `your_project.your_dataset.your_table`
PARTITION BY TIMESTAMP_TRUNC(timestamp_column, MONTH)
AS SELECT * FROM `your_project.your_dataset.source_table`;
```

### 2️⃣ SQL Transformations

You can optimize queries by precomputing some aggregations:

```sql
CREATE OR REPLACE TABLE `your_project.your_dataset.transformed_table` AS
SELECT
  plant_id,
  TIMESTAMP_TRUNC(timestamp_column, WEEK) AS week_start,
  AVG(temperature) AS avg_temp,
  AVG(humidity) AS avg_humidity,
  COUNT(*) AS data_points
FROM `your_project.your_dataset.your_table`
GROUP BY plant_id, week_start;
```



---

## 📌 Deployment Steps

### 1️⃣ **Execute Airflow DAG to Ingest, Clean, and Load Data to BigQuery**
Run the following command to trigger the ETL process using Airflow DAG:

```sh
gcloud auth login
gcloud config set project plant-123456
gcloud composer environments run plant-composer-env --location us-central1 dags trigger -- plant_ai_pipeline
```

### 2️⃣ **Set Up IAM Permissions (One-Time Setup)**
Before deploying, ensure that the **service account** has the necessary permissions.

```sh
gcloud projects add-iam-policy-binding plant-123456 --member=serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com --role=roles/storage.admin && \
gcloud projects add-iam-policy-binding plant-123456 --member=serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com --role=roles/artifactregistry.writer && \
gcloud projects add-iam-policy-binding plant-123456 --member=serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com --role=roles/run.admin && \
```

### 3️⃣ **Trigger Cloud Build for Automated Deployment**
Go to the local directory containing the cloud_build.yaml, Dockerfile and requirements.txt
Cloud Build will **build the Docker image, push it, and deploy it** to Cloud Run in one step.

```sh
gcloud builds submit --config cloud_build.yaml .
```

### 4️⃣ **Verify Cloud Run Deployment**
After deployment, check the **Cloud Run Service URL**:

```sh
gcloud run services describe plant-dashboard --region=us-central1 --format='value(status.url)'
```

or visit the URL displayed in the Cloud Build logs.


### 5️⃣ **Ensure Public Access to Cloud Run**
If Cloud Run is not accessible publicly, grant permissions:

```sh
gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker plant-health-dashboard
```

### ✅ **Deployment Complete!** 🚀
Your **Plant Health Dashboard** is now live at https://plant-health-dashboard-703716144022.us-central1.run.app/ and updates automatically with new sensor data!

