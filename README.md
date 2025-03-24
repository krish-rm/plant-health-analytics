# 🌱 Plant Health Analytics Project

## **Overview**
This project aims to develop an end-to-end data pipeline that enables efficient monitoring of plant health using IoT sensor data, AI/ML analytics, and a web-based dashboard for visualization. The system automates data ingestion, processing, and deployment to provide real-time insights into plant health and environmental factors.

## **Key Features**
✅ **Automated Data Pipeline** → Ingests, cleans, and transforms plant health data.
✅ **Cloud-Based Storage & Processing** → Utilizes **Google Cloud Storage (GCS)** and **BigQuery**.
✅ **Interactive Dashboard** → Built with **Dash (Plotly)**, deployed on **Cloud Run**.
✅ **CI/CD Workflow** → Uses **Cloud Build & Docker** for automated deployments.
✅ **Airflow Orchestration** → **Cloud Composer (Airflow)** manages scheduled data workflows.

## **Project Workflow**
1️⃣ **Ingestion** → Collects weekly sensor data (CSV) and stores it in **GCS**.
2️⃣ **Processing** → Cleans, transforms, and loads structured data into **BigQuery**.
3️⃣ **Visualization** → The **Dash-based dashboard** fetches data from **BigQuery**.
4️⃣ **Deployment** → Uses **Cloud Run** for public access and **Cloud Build** for CI/CD.

## **Tech Stack**
- **Data Processing** → Pandas, PyArrow, BigQuery
- **Cloud Infrastructure** → GCS, BigQuery, Cloud Composer (Airflow)
- **Web Dashboard** → Dash (Plotly), Flask
- **Deployment** → Cloud Run, Docker, Cloud Build, IAM
- **Monitoring & Logging** → Cloud Logging, Cloud Monitoring
- **Infrastructure as Code** (Optional) → Terraform

## **Deployment Instructions**
For detailed deployment steps, refer to [Deployment Guide](docs/deployment_guide.md).

## **Future Enhancements**
✔️ **Real-Time Data Processing** → Integrate **Pub/Sub + Dataflow**.
✔️ **Machine Learning Integration** → Predict plant health trends using **Vertex AI**.
✔️ **Enhanced Security** → Implement **API Gateway & IAP** for secure access.

🚀 **This project provides a scalable and automated system for plant health monitoring using cloud-based data analytics and visualization.**

