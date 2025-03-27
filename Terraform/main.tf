provider "google" {
  project = "plant-123456"
  region  = "us-central1"
}

# 1️⃣ Google Cloud Storage Bucket
resource "google_storage_bucket" "plant_bucket" {
  name     = "plant-bucket-123456"
  location = "US"
  uniform_bucket_level_access = true
}

# 2️⃣ BigQuery Dataset
resource "google_bigquery_dataset" "plant_dataset" {
  dataset_id = "plant_data"
  location   = "US"
}

# 3️⃣ IAM Permissions for BigQuery and Cloud Storage
resource "google_project_iam_member" "bq_data_editor" {
  project = "plant-123456"
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "storage_admin" {
  project = "plant-123456"
  role    = "roles/storage.admin"
  member  = "serviceAccount:plant-service-account@plant-123456.iam.gserviceaccount.com"
}

# 4️⃣ Cloud Run Deployment for Plant Health Dashboard
resource "google_cloud_run_service" "plant_dashboard" {
  name     = "plant-dashboard"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/plant-123456/plant_dashboard:latest"
      }
    }
  }
}

# 5️⃣ IAM Policy to Allow Public Access to Cloud Run
resource "google_cloud_run_service_iam_binding" "public_access" {
  location = google_cloud_run_service.plant_dashboard.location
  service  = google_cloud_run_service.plant_dashboard.name
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}
