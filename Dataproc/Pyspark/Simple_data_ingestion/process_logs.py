from pyspark.sql import SparkSession
from pyspark.sql.functions import split, col, explode

if __name__ == "__main__":
    spark = SparkSession.builder.appName("LogProcessor").getOrCreate()

    # Input and output paths
    input_path = "gs://gcp_charan_learning_1/dataproc-pyspark/input/weblog.txt"    	#change path accordingly
    output_path = "gs://gcp_charan_learning_1/dataproc-pyspark/output/page_views"   #change path accordingly

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
