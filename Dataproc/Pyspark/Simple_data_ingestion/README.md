### Project Goal: 
Read website log files from Google Cloud Storage (GCS), transform them using PySpark within a Dataproc cluster, and write the transformed data (page view counts) back to GCS in Parquet format.
### Prerequisites:

* A Google Cloud Platform (GCP) account with billing enabled.
* Basic understanding of the Google Cloud Console and command-line interface (CLI).
* Basic Python and PySpark knowledge.

### Step-by-Step Guide:

1. Set up Google Cloud Environment:

a. Create a Google Cloud Project (if you don't have one)

b. Enable the Dataproc API:
* In the Cloud Console, navigate to "APIs & Services" -> "Library" (or just search for "APIs & Services").
* Search for "Dataproc API."
* Click on the Dataproc API.
* Click "Enable."

c. Create a Google Cloud Storage (GCS) Bucket:
* In the Cloud Console, navigate to "Storage" -> "Browser" (or search for "Storage").
* Click "Create Bucket."
* Enter a bucket name (e.g., dataproc-pyspark-example). Bucket names must be globally unique across Google Cloud.
* Choose a region that is geographically close to you (e.g., us-central1).
* Choose a storage class (e.g., "Standard" is fine for this project).
* Leave other settings at their defaults and click "Create."
* Create subdirectories inside the bucket named input and output. You can do this through the console or via the gsutil command line utility.

2. Prepare Sample Log Data:

a. Refer to the weblog.txt file with the sample log data, download to your computer.

b. Upload the Log File to GCS:
* Using the Cloud Console: Navigate to your GCS bucket (dataproc-pyspark-example).
* Go to the input directory.
* Click "Upload Files."
* Select the weblog.txt file from your computer.

3. Create the PySpark Script (process_logs.py):
* Create a new Python file named process_logs.py in your local development environment.
* Copy and paste the following code into the process_logs.py file:
  ``` python
  from pyspark.sql import SparkSession
  from pyspark.sql.functions import split, col, explode
  
  if __name__ == "__main__":
      spark = SparkSession.builder.appName("LogProcessor").getOrCreate()
  
      # Input and output paths
      input_path = "gs://dataproc-pyspark-example/input/weblog.txt"
      output_path = "gs://dataproc-pyspark-example/output/page_views"
  
      # Read the log file
      log_df = spark.read.text(input_path)
  
      # Split the log lines into columns
      split_col = split(log_df['value'], ' - ')
      logs_df = log_df.withColumn('timestamp', split_col.getItem(0)) \
                    .withColumn('level', split_col.getItem(1)) \
                    .withColumn('message', split_col.getItem(2))
  
      # Extract the page from the message (simplified)
      logs_df = logs_df.withColumn("page", split(logs_df["message"], " ").getItem(1))
  
      # Filter for page access events
      page_view_df = logs_df.filter(col("message").like("Page % accessed%"))
  
      # Count page views
      page_counts = page_view_df.groupBy("page").count().orderBy("count", ascending=False)
  
      # Write the output to GCS in Parquet format
      page_counts.write.mode("overwrite").parquet(output_path)
  
      page_counts.show() #Show results
  
      spark.stop()
    ```

4. Create a Dataproc Cluster:
* Using the Google Cloud Console: Navigate to "Dataproc" -> "Clusters" in the Cloud Console (or search for "Dataproc").
* Click "Create Cluster."
* Cluster Configuration: Cluster Name: my-dataproc-cluster
* Region: Choose a region close to you (e.g., us-central1).
* Zone: Choose any.
* Cluster Type: "Standard"
* Configure Nodes:
* Master Node: Machine Type: n4-standard-2 (2 vCPU, 8 GB memory) is sufficient for this example.
* Worker Nodes: Number of Workers: 2 or 3 (start with 2 for smaller datasets) Machine Type: n4-standard-2

5. Submit the PySpark Job to Dataproc:
* Using the gcloud Command-Line Tool: Make sure you are in the same directory as process_logs.py when you run the command, or provide the full path to the script.
``` unix
  gcloud dataproc jobs submit pyspark \
      --cluster=my-dataproc-cluster \
      --region=us-central1 \
      process_logs.py
```
6. Verify the Results:
* Using the Google Cloud Console: Navigate to your GCS bucket (dataproc-pyspark-example).
* Go to the output/page_views directory. You should see one or more Parquet files.
