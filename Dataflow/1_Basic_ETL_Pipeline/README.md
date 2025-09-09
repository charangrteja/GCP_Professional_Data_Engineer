# Serverless Data Processing with Dataflow - Writing an ETL Pipeline using Apache Beam and Dataflow (Python)
graph LR
    A[Start] --> B(Parse Arguments);
    B --> C{Are Arguments Valid?};
    C -- Yes --> D(Set Pipeline Options);
    C -- No --> E[Exit: Invalid Arguments];
    D --> F(Define Input/Output);
    F --> G(Create Beam Pipeline);
    G --> H(Read from GCS);
    H --> I(Parse JSON);
    I --> J(Write to BigQuery);
    J --> K(Run Pipeline);
    K --> L[End];
