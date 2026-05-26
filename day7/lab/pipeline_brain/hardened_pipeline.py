import logging
import shutil
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, lit, when, sum, count, max, coalesce, avg, min
from pyspark.sql.types import FloatType, StringType, DateType
import json
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def ingest_bronze(spark, input_path, output_path, run_date, run_id):
    try:
        logging.info("Starting ingest_bronze stage")
        
        # Read raw CSV files with all columns as strings
        transactions_df = (spark.read.format("csv")
                          .option("header", "true")
                          .option("inferSchema", "false")
                          .load(input_path))
        
        logging.info(f"[Stage: ingest_bronze] input_count: {transactions_df.count():,}")
        
        # Add metadata columns
        transactions_df = (transactions_df.withColumn("ingestion_timestamp", lit(run_date))
                           .withColumn("source_file", lit("transactions.csv"))
                          .withColumn("pipeline_run_id", lit(run_id)))
        
        # Delete existing partition before writing
        partition_path = f"{output_path}/ingestion_timestamp={run_date}"
        shutil.rmtree(partition_path, ignore_errors=True)
        
        # Write as Parquet partitioned by date
        transactions_df.write.mode("overwrite").partitionBy("ingestion_timestamp").parquet(output_path)
        
        logging.info(f"[Stage: ingest_bronze] output_count: {transactions_df.count():,}")
        
    except Exception as e:
        logging.error(f"Error in ingest_bronze stage: {e}")
        raise

def transform_silver(spark, bronze_path, merchants_path, output_path, run_date):
    try:
        logging.info("Starting transform_silver stage")
        
        # Read Bronze Parquet with partition pruning on run_date
        transactions_df = (spark.read.format("parquet")
                           .load(bronze_path)
                          .filter(col("ingestion_timestamp") == run_date))
        
        logging.info(f"[Stage: transform_silver] input_count: {transactions_df.count():,}")
        
        # Cast columns to correct types
        transactions_df = (transactions_df.withColumn("amount", col("amount").cast(FloatType()))
                          .withColumn("transaction_date", col("transaction_date").cast(DateType()))
                          .withColumn("transaction_id", col("transaction_id").cast(StringType()))
                          .withColumn("merchant_id", col("merchant_id").cast(StringType())))
        
        # Filter: remove records where transaction_id is NULL or amount < 0
        transactions_df = transactions_df.filter((col("transaction_id").isNotNull()) & (col("amount") >= 0))
        
        logging.info(f"[Stage: transform_silver] after_filter_count: {transactions_df.count():,}")
        
        # Deduplicate: if same transaction_id appears twice, keep the record with latest ingestion_timestamp
        transactions_df = transactions_df.withColumn("rank", 
                                                     when(col("ingestion_timestamp").isNotNull(), 
                                                           col("ingestion_timestamp").cast("long")).otherwise(0).alias("rank"))
        transactions_df = transactions_df.withColumn("row_number", 
                                                     Window.row_number().over(Window.partitionBy("transaction_id").orderBy(col("rank").desc())))
        transactions_df = transactions_df.filter(col("row_number") == 1).drop("rank", "row_number")
        
        logging.info(f"[Stage: transform_silver] after_dedup_count: {transactions_df.count():,}")
        
        # Read merchants data and cache it
        merchants_df = (spark.read.format("csv")
                       .option("header", "true")
                        .option("inferSchema", "false")
                       .load(merchants_path))
        merchants_df = merchants_df.withColumn("merchant_id", col("merchant_id").cast(StringType()))
        merchants_df = merchants_df.cache()
        
        # Enrich: join transactions with merchants on merchant_id
        enriched_df = (transactions_df.join(broadcast(merchants_df), 
                                            on=col("transactions_df.merchant_id") == col("merchants_df.merchant_id"), 
                                            how="left_outer"))
        
        # Add quality flag: mark records with no matching merchant as 'UNMATCHED'
        enriched_df = enriched_df.withColumn("quality_flag", 
                                             when(col("merchant_id").isNotNull(), "CLEAN").otherwise("UNMATCHED"))
        
        # Delete existing partition before writing
        partition_path = f"{output_path}/transaction_date={run_date}"
        shutil.rmtree(partition_path, ignore_errors=True)
        
        # Write as Parquet partitioned by date
        enriched_df.write.mode("overwrite").partitionBy("transaction_date").parquet(output_path)
        
        logging.info(f"[Stage: transform_silver] output_count: {enriched_df.count():,}")
        
    except Exception as e:
        logging.error(f"Error in transform_silver stage: {e}")
        raise

def build_merchant_performance(spark, silver_path, output_path, run_date):
    try:
        logging.info("Starting build_merchant_performance stage")
        
        # Read Silver layer data with partition pruning
        silver_df = spark.read.parquet(silver_path).filter(col("transaction_date") == run_date)
        
        logging.info(f"[Stage: build_merchant_performance] input_count: {silver_df.count():,}")
        
        # Calculate total revenue, transaction count, and failure rate
        merchant_performance_df = silver_df.groupBy("merchant_id", "merchant_name", "category", "city", "transaction_date") \
           .agg(
                sum(when(col("status") == "COMPLETED", col("amount")).otherwise(0)).alias("total_revenue"),
                count("*").alias("txn_count"),
                (count(when(col("status") == "FAILED", 1)) / count("*") * 100).alias("failure_rate_pct")
            )
        
        # Delete existing partition before writing
        partition_path = f"{output_path}/merchant_performance/transaction_date={run_date}"
        shutil.rmtree(partition_path, ignore_errors=True)
        
        # Write Gold layer merchant performance table
        merchant_performance_df.write.mode("overwrite").partitionBy("transaction_date").parquet(output_path + "/merchant_performance")
        
        logging.info(f"[Stage: build_merchant_performance] output_count: {merchant_performance_df.count():,}")
        
    except Exception as e:
        logging.error(f"Error in build_merchant_performance stage: {e}")
        raise

def build_customer_ltv(spark, silver_path, output_path):
    try:
        logging.info("Starting build_customer_ltv stage")
        
        # Read Silver layer data
        silver_df = spark.read.parquet(silver_path)
        
        logging.info(f"[Stage: build_customer_ltv] input_count: {silver_df.count():,}")
        
        # Calculate customer LTV metrics
        customer_ltv_df = silver_df.filter(col("status") == "COMPLETED") \
            .groupBy("customer_id") \
           .agg(
                sum("amount").alias("total_spent"),
                count("*").alias("total_txns"),
                avg("amount").alias("avg_txn_value"),
                min("transaction_date").alias("first_txn_date"),
                max("transaction_date").alias("last_txn_date"),
                coalesce(max("payment_method"), lit(None)).alias("preferred_payment_method")
            )
        
        # Write Gold layer customer LTV table
        customer_ltv_df.write.parquet(output_path + "/customer_ltv")
        
        logging.info(f"[Stage: build_customer_ltv] output_count: {customer_ltv_df.count():,}")
        
    except Exception as e:
        logging.error(f"Error in build_customer_ltv stage: {e}")
        raise

def build_daily_summary(spark, silver_path, output_path, run_date):
    try:
        logging.info("Starting build_daily_summary stage")
        
        # Read Silver layer data with partition pruning
        silver_df = spark.read.parquet(silver_path).filter(col("transaction_date") == run_date)
        
        logging.info(f"[Stage: build_daily_summary] input_count: {silver_df.count():,}")
        
        # Calculate daily summary metrics
        daily_summary_df = silver_df.groupBy("transaction_date") \
            .agg(
                sum(when(col("status") == "COMPLETED", col("amount")).otherwise(0)).alias("total_revenue"),
                count("*").alias("total_txns"),
                countDistinct("customer_id").alias("unique_customers"),
                countDistinct("merchant_id").alias("unique_merchants"),
                (count(when(col("status") == "FAILED", 1)) / count("*") * 100).alias("failure_rate_pct")
            )
        
        # Delete existing partition before writing
        partition_path = f"{output_path}/daily_summary/transaction_date={run_date}"
        shutil.rmtree(partition_path, ignore_errors=True)
        
        # Write Gold layer daily summary table
        daily_summary_df.write.mode("overwrite").partitionBy("transaction_date").parquet(output_path + "/daily_summary")
        
        logging.info(f"[Stage: build_daily_summary] output_count: {daily_summary_df.count():,}")
        
    except Exception as e:
        logging.error(f"Error in build_daily_summary stage: {e}")
        raise

def run_gold(spark, silver_path, gold_output_dir, run_date):
    try:
        logging.info("Starting run_gold stage")
        
        # Build Gold layer tables
        build_merchant_performance(spark, silver_path, gold_output_dir, run_date)
        build_customer_ltv(spark, silver_path, gold_output_dir)
        build_daily_summary(spark, silver_path, gold_output_dir, run_date)
        
        # Write run metadata summary
        run_metadata = {
            "run_date": run_date,
            "silver_path": silver_path,
            "gold_output_dir": gold_output_dir,
            "status": "success"
        }
        spark.sparkContext.parallelize([run_metadata]).write.json(gold_output_dir + "/run_metadata")
        
    except Exception as e:
        logging.error(f"Error in run_gold stage: {e}")
        raise

def main():
    # Initialize Spark session
    spark = (SparkSession.builder
            .appName("Sigma DataTech Transaction Analytics Pipeline")
             .getOrCreate())
    
    # Define paths and run metadata
    input_path = "s3://sigma-datatech-raw/transactions/"
    bronze_path = "s3://sigma-datatech-bronze/transactions/"
    merchants_path = "s3://sigma-datatech-bronze/merchants/"
    silver_path = "s3://sigma-datatech-silver/transactions/"
    gold_output_dir = "s3://sigma-datatech-gold/transactions/"
    run_date = "2026-05-27"
    run_id = "run_id_12345"
    
    started_at = datetime.now().isoformat()
    
    try:
        # Ingest Bronze layer
        ingest_bronze(spark, input_path, bronze_path, run_date, run_id)
        
        # Transform Silver layer
        transform_silver(spark, bronze_path, merchants_path, silver_path, run_date)
        
        # Run Gold layer
        run_gold(spark, silver_path, gold_output_dir, run_date)
        
        completed_at = datetime.now().isoformat()
        
        run_metadata = {
            "pipeline_name": "Sigma DataTech Transaction Analytics Pipeline",
            "run_date": run_date,
            "run_id": run_id,
            "run_status": "SUCCESS",
            "started_at": started_at,
            "completed_at": completed_at
        }
        
        with open(f"s3://sigma-datatech-metadata/run_metadata_{run_date}.json", "w") as f:
            json.dump(run_metadata, f)
            
    except Exception as e:
        completed_at = datetime.now().isoformat()
        
        run_metadata = {
            "pipeline_name": "Sigma DataTech Transaction Analytics Pipeline",
            "run_date": run_date,
            "run_id": run_id,
            "run_status": "FAILED",
            "error_message": str(e),
            "started_at": started_at,
            "completed_at": completed_at
        }
        
        with open(f"s3://sigma-datatech-metadata/run_metadata_{run_date}.json", "w") as f:
            json.dump(run_metadata, f)

if __name__ == "__main__":
    main()
