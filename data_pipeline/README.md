# Data Pipeline for Aggregating Tourist Attractions

This directory contains the scripts and resources for the data pipeline that fetches tourist attraction data from various sources, cleans it, and upserts it into the Supabase database.

## Overview

The main goal of this pipeline is to create a unified and de-duplicated database of tourist attractions. It is designed to be run as a scheduled job (e.g., Cron Job) or triggered manually.

The pipeline performs the following steps:
1.  **Fetch Data**: Retrieves data from one or more sources (e.g., external APIs, CSV files).
2.  **Transform Data**: Cleans the raw data and maps it to the `attractions` table schema in the database.
3.  **Upload Images**: Downloads the main image for each attraction, uploads it to Supabase Storage, and stores the public URL.
4.  **Upsert Record**: Inserts or updates the attraction record in the database. It uses a unique constraint on `(source, source_id)` to prevent duplicates.
5.  **Log Output**: Logs its progress and any errors to `data_pipeline.log`.

## Setup

1.  **Environment Variables**: The pipeline requires credentials to be set in an `.env` file in the project root. Copy the main `.env.example` to `.env` and fill in the required values. The pipeline specifically needs:
    ```bash
    # Supabase credentials for the data pipeline
    SUPABASE_URL="https://your-project-ref.supabase.co"
    SUPABASE_SERVICE_KEY="your-supabase-service-role-key"
    ```

2.  **Dependencies**: Ensure all Python dependencies are installed by running the following command from the project root:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the Pipeline

To execute the entire data pipeline, run the main script from the project root directory:

```bash
python data_pipeline/run_pipeline.py
```

The script will log its output to both the console and the `data_pipeline.log` file.

## How to Add a New Data Source

The pipeline is designed to be modular, making it easy to add new data sources.

1.  **Create a Fetcher Module**:
    -   In the `data_pipeline/sources/` directory, create a new Python file (e.g., `new_api_source.py`).
    -   Inside this file, create a function called `fetch_data()` that contains the logic for fetching data from your new source.
    -   This function should return a list of dictionaries, where each dictionary represents a raw attraction record.

2.  **Create a Transformer**:
    -   The `transform_data()` function in `run_pipeline.py` is designed to map fields. You may need to adjust it or create a new one if the new data source has a significantly different structure. The goal is to produce a clean dictionary that matches the `attractions` table schema.

3.  **Integrate into the Main Script**:
    -   Open `data_pipeline/run_pipeline.py`.
    -   Import your new `fetch_data` function.
    -   In the `main()` function, call your new fetcher and process its results. You should assign a unique `source_name` for each source to ensure the `(source, source_id)` constraint works correctly.
