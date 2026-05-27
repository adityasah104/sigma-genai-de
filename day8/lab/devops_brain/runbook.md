<<<<<<< HEAD
# Pipeline Overview

This pipeline ingests transaction data, transforms it into a cleaned and enriched format, and computes merchant performance and daily summary metrics. It runs to ensure data is up-to-date for downstream analytics and reporting. If it stops, critical business metrics and reports will be outdated.

## Pipeline Steps

1. Connect to DuckDB database using `get_connection()`.
2. Set up required tables using `setup_tables()`.
3. Load merchants data using `load_merchants()`.
4. Load raw transactions into the bronze table using `load_bronze()`.
5. Transform bronze transactions to silver using `transform_bronze_to_silver()`.
6. Load transformed transactions into the silver table using `load_silver()`.
7. Compute merchant performance metrics using `compute_merchant_performance()`.
8. Compute daily summary metrics using `compute_daily_summary()`.
9. Load computed metrics into gold tables using `load_gold()`.

## Schedule / Trigger

This pipeline runs every hour, triggered by a cron job.

## Failure Modes

1. **Database Connection Failure**
   - **Root Cause:** DuckDB service is down.
   - **Symptom:** `get_connection()` raises an exception.
2. **Table Creation Failure**
   - **Root Cause:** Syntax error in SQL.
   - **Symptom:** `setup_tables()` raises an exception.
3. **Merchant Data Load Failure**
   - **Root Cause:** Corrupted merchant data.
   - **Symptom:** `load_merchants()` raises an exception.
4. **Bronze Table Load Failure**
   - **Root Cause:** Malformed transaction data.
   - **Symptom:** `load_bronze()` raises an exception.
5. **Silver Table Transformation Failure**
   - **Root Cause:** Missing merchant mapping.
   - **Symptom:** `transform_bronze_to_silver()` raises an exception.

## Recovery Actions

1. **Database Connection Failure**
   - Check DuckDB service status.
   - Restart DuckDB service if down.
   - Retry pipeline.
2. **Table Creation Failure**
   - Review SQL syntax in `setup_tables()`.
   - Fix SQL errors.
   - Retry pipeline.
3. **Merchant Data Load Failure**
   - Validate merchant data integrity.
   - Correct any data issues.
   - Retry pipeline.
4. **Bronze Table Load Failure**
   - Inspect transaction data for errors.
   - Correct malformed records.
   - Retry pipeline.
5. **Silver Table Transformation Failure**
   - Ensure all merchants are mapped.
   - Add missing merchant mappings.
   - Retry pipeline.

## Known Bugs

- Hardcoded AWS credentials in the code.
- Lack of null handling in `transform_bronze_to_silver()`.

## Escalation Contacts

=======
# Transaction Pipeline Runbook

## Pipeline Overview
This pipeline processes transaction data, transforming it from bronze to silver and finally to gold layers. It runs to ensure data is cleansed, enriched, and summarized for reporting and analytics. If this pipeline stops, downstream reports and dashboards will lack updated data, impacting decision-making.

## Pipeline Steps
1. Connect to the DuckDB database using `get_connection()`.
2. Set up necessary tables using `setup_tables(con)`.
3. Load merchant data into the `merchants` table using `load_merchants(con)`.
4. Load transactions into the `bronze_transactions` table using `load_bronze(con, transactions)`.
5. Transform bronze transactions to silver using `transform_bronze_to_silver(transactions, merchants)`.
6. Load transformed data into the `silver_transactions` table using `load_silver(con, silver_rows)`.
7. Compute merchant performance metrics using `compute_merchant_performance(silver_rows)`.
8. Compute daily summary metrics using `compute_daily_summary(silver_rows)`.
9. Load performance and summary data into gold tables using `load_gold(con, merchant_perf, daily_summary)`.

## Schedule / Trigger
This pipeline runs daily at 2 AM UTC via a cron job.

## Failure Modes
1. **Database Connection Failure**
   - **Root Cause:** Incorrect database path or permissions.
   - **Symptom:** Pipeline fails to start.
2. **Table Creation Error**
   - **Root Cause:** Syntax error in SQL.
   - **Symptom:** Pipeline stops at `setup_tables`.
3. **Merchant Data Load Failure**
   - **Root Cause:** Corrupt or missing merchant data.
   - **Symptom:** Pipeline stops at `load_merchants`.
4. **Bronze Transaction Load Failure**
   - **Root Cause:** Malformed transaction data.
   - **Symptom:** Pipeline stops at `load_bronze`.
5. **Silver Transformation Failure**
   - **Root Cause:** Inconsistent data types or missing fields.
   - **Symptom:** Pipeline stops at `transform_bronze_to_silver`.

## Recovery Actions
1. **Database Connection Failure**
   - Verify DB_PATH and permissions.
   - Restart the pipeline.
2. **Table Creation Error**
   - Check SQL syntax in `setup_tables`.
   - Correct the error and rerun the pipeline.
3. **Merchant Data Load Failure**
   - Validate `MERCHANTS` data.
   - Fix any issues and rerun the pipeline.
4. **Bronze Transaction Load Failure**
   - Inspect `TRANSACTIONS_CLEAN` and `TRANSACTIONS_DIRTY` for errors.
   - Correct data and rerun the pipeline.
5. **Silver Transformation Failure**
   - Review data types and fields in `transform_bronze_to_silver`.
   - Fix inconsistencies and rerun the pipeline.

## Known Bugs
- Hardcoded AWS credentials in the code.
- Lack of null handling in `transform_bronze_to_silver`.

## Escalation Contacts
>>>>>>> 792b7e2 (Day8 completed)
1. **On-call DE:** Priya Nair (priya.nair@sigmadatatech.in, +91-98400-11111)
2. **Tech Lead:** Arjun Mehta (arjun.mehta@sigmadatatech.in)
3. **Platform Manager:** Kavya Reddy (kavya.reddy@sigmadatatech.in)

## Data Quality Checks
<<<<<<< HEAD

- Verify the number of records in `silver_transactions` matches expected count.
- Check `gold_merchant_performance` for accurate merchant metrics.
- Ensure `gold_daily_summary` reflects current date's data.
=======
- Verify the count of records in `bronze_transactions`, `silver_transactions`, `gold_merchant_performance`, and `gold_daily_summary`.
- Ensure `quality_flag` is correctly set in `silver_transactions`.
- Check for any NULL values in critical fields.
- Validate the sums and counts in `gold_merchant_performance` and `gold_daily_summary`.
>>>>>>> 792b7e2 (Day8 completed)
