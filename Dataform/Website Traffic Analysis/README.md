# WEBSITE TRAFFIC ANALYSIS USING DATAFORM
### Prerequisites:
* A Google Cloud project with Dataform enabled.
* A BigQuery dataset to store your data.
* Access to Google Analytics data (or sample CSV data as a substitute).
* Basic familiarity with SQL and JavaScript.
### Step 1: Set Up Your Dataform Project

1. Create a New Dataform Repository:
* In the Google Cloud Console, navigate to Dataform.
* Click "Create Repository."
* Give your repository a name (e.g., dataform-repository).
* Select a region (e.g., us-central1).
2. Create a Development Workspace:
* In the Dataform repository, click "Create Development Workspace."
* Give your workspace a name (e.g., my-dataform-workspace).
### Step 2: Load Data into BigQuery (Staging)
1. You can either use Bigquery public datasets or upload your own files. For the purpose of this project, we will use the csv files ga_sessions.txt and ga_pageviews.txt
2. Upload CSV Files to BigQuery:
* In the Google Cloud Console, navigate to BigQuery.
* Select your dataset. If you do not have one, create one (e.g., raw_source_files) in us-central1 region to be consistent with your dataform repository.
* Click "Create Table."
* Choose "Upload" as the source.
* Select "CSV" as the file format.
* Upload ga_sessions.txt.
* Give the table a name (e.g., raw_ga_sessions).
* Specify the schema (either manually or let BigQuery auto-detect it). Important: Ensure data types are correct (e.g., session_start_time should be DATETIME).
* Repeat for ga_pageviews.txt, naming the table raw_ga_pageviews.
### Step 3: Create Staging Tables in Dataform
1. Create a new file named definitions/staging/stg_ga_sessions.sqlx:
``` SQL
config {
  type: "table",
  name: "stg_ga_sessions",
  description: "Staged Google Analytics session data."
}

SELECT
  CAST(session_id AS INT64) AS session_id,
  user_id,
  CAST(session_start_time AS DATETIME) AS session_start_time,
  CAST(pageviews AS INT64) AS pageviews,
  country
FROM
  ${ref("raw_ga_sessions")}
```
