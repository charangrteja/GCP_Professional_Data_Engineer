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
You can either use Bigquery public datasets or upload your own files. For the purpose of this project, we will use the csv files ga_sessions.txt and ga_pageviews.txt 
