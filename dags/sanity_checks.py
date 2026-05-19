from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# 1. Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 2. Initialize the DAG
with DAG(
    'airflow_sanity_check',
    default_args=default_args,
    description='A simple DAG to test if Airflow is working',
    schedule_interval=None,  # None means it will only run when manually triggered
    catchup=False,
    tags=['test'],
) as dag:

    # 3. Define the task
    test_task = BashOperator(
        task_id='print_test_message',
        bash_command='echo "Success! Airflow is executing tasks correctly."',
    )

    # Note: Since there's only one task, we don't strictly need to set dependencies,
    # but this is where you would normally put `test_task`
    test_task