from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession.builder.appName("ReadOutput").getOrCreate()

    output_path = "gs://gcp_charan_learning_1/dataproc-pyspark/output/page_views" #change path accordingly

    # Read the Parquet files
    output_df = spark.read.parquet(output_path)

    # Show the results
    output_df.show()

    spark.stop()
