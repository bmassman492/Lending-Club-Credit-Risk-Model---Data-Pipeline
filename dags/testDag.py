from airflow.sdk import DAG, task
from datetime import datetime

with DAG(
    dag_id="testDag",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["test"],
) as dag:
    
    @task
    def say_hello():
        print("Hello from Airflow!")
    
    say_hello()
