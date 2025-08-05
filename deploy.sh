#!/bin/bash
# Exit on any error
set -e

# --- Set your configuration variables ---
# The GCS bucket that will trigger the function
export BUCKET_NAME="cloud_functions_ct"

# The name you want to give your Cloud Function
export FUNCTION_NAME="gcs_to_bigquery"

# Your BigQuery dataset and table IDs
export BIGQUERY_DATASET="charan_sandbox"
export BIGQUERY_TABLE="employee_details"

# The region to deploy your function and resources
export REGION="us-central1"

# --- Project and Service Account Configuration ---
export GCP_PROJECT=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe ${GCP_PROJECT} --format='value(projectNumber)')
export COMPUTE_ENGINE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# --- Script logic ---

echo "Enabling required services..."

gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  artifactregistry.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

echo "Checking and creating GCS bucket: ${BUCKET_NAME}..."
# Create GCS bucket if it doesn't exist
gcloud storage buckets describe gs://${BUCKET_NAME} >/dev/null 2>&1 || \
  gcloud storage buckets create gs://${BUCKET_NAME} --location=${REGION} --project=${GCP_PROJECT}

echo "Checking and creating BigQuery dataset: ${BIGQUERY_DATASET}..."
# Create BigQuery dataset if it doesn't exist
bq --location=${REGION} show --dataset ${GCP_PROJECT}:${BIGQUERY_DATASET} >/dev/null 2>&1 || \
  bq --location=${REGION} mk --dataset ${GCP_PROJECT}:${BIGQUERY_DATASET}

echo "Granting permissions to the Compute Engine default service account..."

# Grant permissions to the function's runtime service account to run BQ jobs and edit data
gcloud projects add-iam-policy-binding ${GCP_PROJECT} \
  --member="serviceAccount:${COMPUTE_ENGINE_SA}" \
  --role="roles/bigquery.jobUser" \
  --condition=None

echo "Granting BigQuery service permission to read from GCS bucket..."

# Grant the BigQuery service agent permission to read from the GCS bucket
# This is a common step that is easily missed!

BIGQUERY_SERVICE_ACCOUNT="service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com"
gsutil iam ch serviceAccount:${BIGQUERY_SERVICE_ACCOUNT}:roles/storage.objectViewer gs://${BUCKET_NAME}

# Grant Pub/Sub Publisher role to GCS service account
echo "Granting Pub/Sub Publisher role to $BIGQUERY_SERVICE_ACCOUNT..."
gcloud projects add-iam-policy-binding $GCP_PROJECT \
--member="serviceAccount:${BIGQUERY_SERVICE_ACCOUNT}" \
--role="roles/pubsub.publisher" \
--quiet

echo "Creating BigQuery table if it doesn't exist..."
bq query --use_legacy_sql=false "
CREATE TABLE IF NOT EXISTS \`$GCP_PROJECT.$BIGQUERY_DATASET.$BIGQUERY_TABLE\` (
  id INT64,
  name STRING,
  email STRING
);"

echo "Deploying the function..."

# --- Deploy the function ---
# This will use the Compute Engine default service account by default for 2nd Gen functions
gcloud functions deploy ${FUNCTION_NAME} \
  --runtime python311 \
  --region ${REGION} \
  --source . \
  --entry-point gcs_to_bigquery \
  --trigger-resource ${BUCKET_NAME} \
  --trigger-event google.storage.object.finalize \
  --set-env-vars "GCP_PROJECT=$GCP_PROJECT,BIGQUERY_DATASET_ID=$BIGQUERY_DATASET,BIGQUERY_TABLE_ID=$BIGQUERY_TABLE"
