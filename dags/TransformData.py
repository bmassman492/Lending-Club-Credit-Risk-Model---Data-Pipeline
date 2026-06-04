from airflow.sdk import DAG, task
from datetime import datetime
import subprocess

@task
def run_dbt():
    subprocess.run(
        ["/home/airflow/.local/bin/dbt","run",
        "--project-dir", "/opt/airflow/credit_risk_dbt",
        "--profiles-dir", "/opt/airflow/credit_risk_dbt"],
        check=True
    )

@task
def test_dbt():
    subprocess.run(
        ["/home/airflow/.local/bin/dbt","test",
        "--project-dir", "/opt/airflow/credit_risk_dbt",
        "--profiles-dir", "/opt/airflow/credit_risk_dbt"],
        check=True
    )

with DAG(
    dag_id="dbt_transform",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["transformation", "recurring"]
) as dag:

    run_dbt() >> test_dbt()