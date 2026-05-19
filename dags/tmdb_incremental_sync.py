from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.incremental_load import run_pipeline

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="tmdb_incremental_sync",
    description="Incrementally sync TMDB changes into PostgreSQL",
    default_args=default_args,
    start_date=datetime(2026, 5, 1),
    schedule="@daily",
    catchup=False,
    tags=["tmdb", "movies", "ingestion"],
) as dag:

    incremental_sync = PythonOperator(
        task_id="incremental_sync_pipeline",
        python_callable=run_pipeline,
    )

    incremental_sync