import os
from google.cloud import bigquery

def gcs_to_bigquery(event, context):
    """
    Triggered by a file upload to a Cloud Storage bucket.
    This function loads a file from GCS into a BigQuery table.

    Args:
        event (dict): Event payload. The Cloud Functions event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    # Get the GCS bucket and file name from the event
    bucket_name = event['bucket']
    file_name = event['name']
    
    print(f"Processing file: {file_name} from bucket: {bucket_name}.")

    # --- Configuration from Environment Variables ---
    # Get the project ID from the function's execution environment
    project_id = os.environ.get('GCP_PROJECT')
    dataset_id = os.environ.get('BIGQUERY_DATASET_ID')
    table_id = os.environ.get('BIGQUERY_TABLE_ID')

    if not all([project_id, dataset_id, table_id]):
        error_message = "Error: Missing required environment variables (GCP_PROJECT, BIGQUERY_DATASET_ID, BIGQUERY_TABLE_ID)."
        print(error_message)
        raise ValueError(error_message)

    # ---------------------------------------------

    client = bigquery.Client()
    table_ref = client.dataset(dataset_id, project=project_id).table(table_id)
    
    gcs_uri = f'gs://{bucket_name}/{file_name}'

    # Configure the BigQuery load job
    job_config = bigquery.LoadJobConfig()
    
    # Set the source format. Options include:
    # bigquery.SourceFormat.CSV, NEWLINE_DELIMITED_JSON, AVRO, PARQUET, ORC
    # For this example, we'll assume the file is a CSV.
    job_config.source_format = bigquery.SourceFormat.CSV
    
    # Let BigQuery autodetect the schema. For production, it's better
    # to define the schema explicitly for consistency and performance.
    job_config.autodetect = True
    
    # Set the write disposition. Options include:
    # WRITE_TRUNCATE (overwrite), WRITE_APPEND (add), WRITE_EMPTY (fail if not empty)
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    
    # For CSV files, you can specify to skip the header row.
    job_config.skip_leading_rows = 1

    print(f"Starting BigQuery load job from {gcs_uri} to {project_id}.{dataset_id}.{table_id}")

    try:
        # Start the load job
        load_job = client.load_table_from_uri(
            gcs_uri,
            table_ref,
            job_config=job_config
        )
        print(f"Submitted load job: {load_job.job_id}")

        # Wait for the job to complete.
        load_job.result()

        print(f"Job finished. Loaded {load_job.output_rows} rows into {dataset_id}:{table_id}.")

    except Exception as e:
        print(f"Error loading data into BigQuery: {e}")
        # Re-raise the exception to signal a failure to Cloud Functions
        raise

