from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email_smtp
import logging
import json

default_args = {
    'owner': 'data-engineering',
   'retries': 2,
   'retry_delay': timedelta(minutes=5),
    'email_on_failure': True
}

def on_failure_callback(context):
    dag_id = context['dag'].dag_id
    task_id = context['task_instance'].task_id
    execution_date = context['execution_date']
    error_message = context['exception']
    logging.error(f"Dag ID: {dag_id}, Task ID: {task_id}, Execution Date: {execution_date}, Error: {error_message}")
    send_email_smtp(to='alerts@example.com', subject=f"Airflow Task Failed - {dag_id}", html_content=f"Task {task_id} failed on {execution_date}. Error: {error_message}")

def sla_miss_callback(context):
    dag_id = context['dag'].dag_id
    execution_date = context['execution_date']
    logging.error(f"Dag ID: {dag_id}, Execution Date: {execution_date}, SLA Miss")
    send_email_smtp(to='alerts@example.com', subject=f"Airflow SLA Miss - {dag_id}", html_content=f"SLA miss for DAG {dag_id} on {execution_date}")

def extract_bronze(**context):
    """Ingest raw CSVs to Bronze Parquet"""
    ti = context['task_instance']
    ti.xcom_push(key='run_id', value=ti.run_id)
    logging.info(f"{ti} - Extracting Bronze layer started")
    # Implement CSV to Parquet transformation here
    logging.info(f"{ti} - Extracting Bronze layer completed")

def transform_silver(**context):
    """Clean, enrich, deduplicate to Silver"""
    ti = context['task_instance']
    run_id = ti.xcom_pull(task_ids='extract_bronze', key='run_id')
    logging.info(f"{ti} - Transforming Silver layer started with run_id: {run_id}")
    # Implement Silver layer transformation here
    logging.info(f"{ti} - Transforming Silver layer completed")

def build_gold(**context):
    """Generate the 3 Gold aggregation tables"""
    ti = context['task_instance']
    run_id = ti.xcom_pull(task_ids='transform_silver', key='run_id')
    logging.info(f"{ti} - Building Gold layer started with run_id: {run_id}")
    # Implement Gold layer transformation here
    logging.info(f"{ti} - Building Gold layer completed")

with DAG(
    dag_id='sigma_transaction_pipeline',
    schedule='0 2 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    on_failure_callback=on_failure_callback,
    sla_miss_callback=sla_miss_callback,
    tags=['sigma', 'transactions', 'daily'],
    description="Daily Bronze->Silver->Gold pipeline for Sigma DataTech transactions"
) as dag:

    extract_bronze_task = PythonOperator(
        task_id='extract_bronze',
        python_callable=extract_bronze,
        on_failure_callback=on_failure_callback
    )

    transform_silver_task = PythonOperator(
        task_id='transform_silver',
        python_callable=transform_silver,
        on_failure_callback=on_failure_callback
    )

    build_gold_task = PythonOperator(
        task_id='build_gold',
        python_callable=build_gold,
        on_failure_callback=on_failure_callback
    )

    extract_bronze_task >> transform_silver_task >> build_gold_task
