# WEBSITE TRAFFIC ANALYSIS USING DATAFORM
![flow chart](https://github.com/charangrteja/GCP_Professional_Data_Engineer/blob/main/Dataform/Website%20Traffic%20Analysis/webtraffic_dataform.png)
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
* In this step, the data will be read from the raw_ga_sessions table created earlier in the raw_source_files bigquery dataset and loaded into the staging table stg_ga_sessions in dataform dataset. 
* Dataform would naturally try to look for this table in the defaultdataset defined in the workflow_settings.yaml but, as as we are trying to read the raw files from a different dataset, we would have to create a declaration file to specify database, schema and name.
* Create a file definitions/staging/raw_ga_sessions_declaration.sqlx
  ``` js
  config {
    type: "declaration",
    database: "your-bigquery-database", //replace with your bigquery database name
    schema: "raw_source_files",
    name: "raw_ga_sessions"
  }
  ```
2. Create a new file named definitions/staging/stg_ga_pageviews.sqlx:
``` SQL
config {
  type: "table",
  name: "stg_ga_pageviews",
  description: "Staged Google Analytics pageview data."
}

SELECT
  CAST(session_id AS INT64) AS session_id,
  page_url
FROM
  ${ref("raw_ga_pageviews")}  -- Replace with your GA4 table if applicable
```
* Create a similar declaration file definitions/staging/raw_ga_pageviews_declaration.sqlx
    ``` js
  config {
    type: "declaration",
    database: "your-bigquery-database", //replace with your bigquery database name
    schema: "raw_source_files",
    name: "raw_ga_pageviews"
  }
  ```
### Step 4: Create Core Tables (Transformations)
1. Create a new file named definitions/core/sessions_by_country.sqlx:
``` SQL
config {
  type: "table",
  name: "sessions_by_country",
  description: "Aggregated session data by country."
}

SELECT
  country,
  COUNT(DISTINCT session_id) AS total_sessions,
  AVG(pageviews) AS average_pageviews_per_session
FROM
  ${ref("stg_ga_sessions")}
GROUP BY
  country
ORDER BY
  total_sessions DESC
```
2. Create a new file named definitions/core/top_pages.sqlx:
``` SQL
config {
  type: "table",
  name: "top_pages",
  description: "Top visited pages."
}

SELECT
  page_url,
  COUNT(DISTINCT session_id) AS total_sessions
FROM
  ${ref("stg_ga_pageviews")}
GROUP BY
  page_url
ORDER BY
  total_sessions DESC
LIMIT 10  -- Limit to the top 10 pages
```
### Step 5: Add Data Quality Tests
1. Create a new file named definitions/tests/stg_ga_sessions_tests.sqlx:
``` SQL
config {
  type: "assertion",
  name: "stg_ga_sessions_no_null_country"
}

SELECT * FROM ${ref("stg_ga_sessions")} WHERE country IS NULL
```
2. Create a new file named definitions/tests/stg_ga_sessions_positive_pageviews.sqlx:
``` SQL
config {
  type: "assertion",
  name: "stg_ga_sessions_positive_pageviews"
}

SELECT * FROM ${ref("stg_ga_sessions")} WHERE pageviews < 0
```
### Step 6: Run Your Dataform Project
1. Trigger a Run: In your Dataform development workspace, click "Start Execution."
2. Select Targets: Choose the tables and tests you want to run (or select all).
3. View Results: Monitor the execution progress. Check for any errors in the logs. If your tests fail, investigate and fix the issues in your data or code.

### Step 7: Add a Workflow Configuration (for Scheduling)
1. Create a Workflow Configuration:
* In the Dataform repository, go to the "Workflow configurations" tab.
* Click "Create Workflow Configuration."
* Give it a name (e.g., daily_run).
* Select the region.
* Set the cron schedule (e.g., 0 6 * * * for 6:00 AM UTC daily).
* Select the targets to run (all tables and tests).
* Save the configuration.

### END: You have successfully configured dataform repository, development space, extracted raw data, Loaded into staging area, transformed the data and scheduled workflow.
