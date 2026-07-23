from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "/opt/airflow/tmdwh"
DBT_PROFILES_DIR = "/opt/airflow/tmdwh"

default_args = {
    "owner": "airflow",
}

with DAG(
    dag_id="dbt_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["dbt", "postgres"],
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"""
        cd {DBT_PROJECT_DIR} &&
        dbt run --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"""
        cd {DBT_PROJECT_DIR} &&
        dbt test --profiles-dir {DBT_PROFILES_DIR}
        """,
    )

    dbt_run >> dbt_test