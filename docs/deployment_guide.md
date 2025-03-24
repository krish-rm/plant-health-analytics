# 🚀 Deployment Guide for Plant Health Dashboard

The Plant Health Dashboard processes plant health environmental sensor data collected four times (morning, afternoon, evening, night) daily. and weekly . This data is stored in **Google Cloud Storage (GCS)**, where it is ingested, cleaned, and transformed for weekly analysis (e.g., Week 46, 47, …), before being loaded into **BigQuery**. The **Airflow DAG** automates this batch processing, ensuring that the dashboard reflects up-to-date plant health insights.


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
- **Google Cloud Project** (`plant-454208`) is active (`gcloud config set project plant-454208`).  
- **Cloud Storage Bucket** (`gs://plant-ai-bucket-454208`) created for raw and processed data.  
- **BigQuery Dataset** exists to store processed data.  
- **Cloud Composer (Airflow) environment** is set up for DAG execution.  
- **Cloud Composer, Cloud Run and Cloud Build APIs** are enabled:  

  ```sh
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com composer.googleapis.com
  ```  

---

## 📌 Deployment Steps

### 1️⃣ **Execute Airflow DAG to Ingest, Clean, and Load Data to BigQuery**
Run the following command to trigger the ETL process using Airflow DAG:

```sh
gcloud auth login
gcloud config set project plant-454208
gcloud composer environments run plant-composer-env --location us-central1 dags trigger -- plant_ai_pipeline
```

### 2️⃣ **Set Up IAM Permissions (One-Time Setup)**
Before deploying, ensure that the **service account** has the necessary permissions.

```sh
gcloud projects add-iam-policy-binding plant-454208 --member=serviceAccount:plant-service-account@plant-454208.iam.gserviceaccount.com --role=roles/storage.admin && \
gcloud projects add-iam-policy-binding plant-454208 --member=serviceAccount:plant-service-account@plant-454208.iam.gserviceaccount.com --role=roles/artifactregistry.writer && \
gcloud projects add-iam-policy-binding plant-454208 --member=serviceAccount:plant-service-account@plant-454208.iam.gserviceaccount.com --role=roles/run.admin && \
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

