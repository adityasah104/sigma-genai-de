<<<<<<< HEAD
# Data Pipeline Design Document

## What This Pipeline Does
This pipeline ingests transaction data from both clean and dirty sources, processes it, and stores it in three layers: Bronze, Silver, and Gold. The Bronze layer stores raw data, the Silver layer stores cleaned and enriched data, and the Gold layer stores aggregated metrics.
=======
# Pipeline Design Document

## What This Pipeline Does
This pipeline ingests transaction data from both clean and dirty sources, processes it, and generates merchant performance and daily summary reports.
>>>>>>> 792b7e2 (Day8 completed)

## Data Flow Diagram

```
<<<<<<< HEAD
+----------------+      +--------------------+      +--------------------+      +--------------------+
| TRANSACTIONS   | ---> | bronze_transactions| ---> | silver_transactions| ---> | gold_merchant_perf |
| (Clean & Dirty)|      |                    |      |                    |      |                    |
+----------------+      +--------------------+      +--------------------+      +--------------------+
                                                                                     |
                                                                                 +--------------------+
                                                                                 | gold_daily_summary  |
                                                                                 +--------------------+
```

## Key Design Decisions
- **Layered Approach**: The pipeline uses a three-tier architecture (Bronze, Silver, Gold) to separate raw data, cleaned data, and aggregated metrics.
- **Data Enrichment**: The Silver layer enriches transaction data by joining it with merchant information, making it more useful for analysis.
- **Aggregation**: The Gold layer computes metrics like merchant performance and daily summaries, providing valuable insights.
- **Data Quality Flags**: The Silver layer includes quality flags to distinguish between clean and potentially problematic data.

## Known Limitations
- **Data Duplication**: The pipeline does not handle duplicate transactions within a single run.
- **Limited Error Handling**: The pipeline has minimal error handling, which could be improved for robustness.
- **Single-Run Processing**: The pipeline processes all transactions in a single run, which may not be suitable for very large datasets.
- **Static Merchant Data**: Merchant data is loaded once and not updated unless the pipeline is rerun.

## Dependencies
- **DuckDB**: The pipeline uses DuckDB for data storage and processing.
- **MERCHANTS**: A list of merchant data used for enriching transactions.
- **TRANSACTIONS_CLEAN and TRANSACTIONS_DIRTY**: Lists of clean and dirty transaction data, respectively.
=======
+--------------------+     +--------------------+     +--------------------+     +--------------------+
| Source:            |     | Bronze:            |     | Silver:            |     | Gold:              |
| TRANSACTIONS_CLEAN | --> | bronze_transactions| --> | silver_transactions| --> | gold_merchant_perf |
| TRANSACTIONS_DIRTY  |     |                    |     |                    |     | gold_daily_summary |
+--------------------+     +--------------------+     +--------------------+     +--------------------+
```

## Key Design Decisions
- **Layered Processing**: The pipeline uses a three-layer approach (Bronze, Silver, Gold) to ensure data quality and transformation are handled separately.
- **Data Quality Flags**: Introduced quality flags in the Silver layer to distinguish between clean and potentially problematic data.
- **Aggregations in Gold**: Aggregations and summaries are computed in the Gold layer to provide high-level insights.
- **Use of DuckDB**: DuckDB is chosen for its lightweight and efficient performance, suitable for both development and production environments.

## Known Limitations
- **Single Source**: The pipeline currently supports only one source of transaction data. Adding more sources would require modifications.
- **Static Merchant Data**: Merchant data is loaded once and not updated dynamically. This could lead to discrepancies if merchant information changes.
- **No Error Handling**: The pipeline lacks comprehensive error handling, which could lead to data loss in case of failures.
- **No Incremental Loads**: The pipeline performs a full load every run, which may not be efficient for large datasets.

## Dependencies
- **DuckDB**: Database engine for storing and processing data.
- **MERCHANTS**: A list of merchant data used for enriching transaction records.
- **TRANSACTIONS_CLEAN and TRANSACTIONS_DIRTY**: Source transaction data files.
- **AWS S3**: Not directly used in the provided code but mentioned in the initial imports, indicating potential future integration.
>>>>>>> 792b7e2 (Day8 completed)
