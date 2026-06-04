from airflow.sdk import DAG, task
from datetime import datetime
from extractFREDDataScript import extract_data, transfer_data

with DAG (
    dag_id="FREDMacroeconomicData",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["extraction", "recurring"]
) as dag:


    extract = task(extract_data, task_id="extract")()
    transfer = task(transfer_data, task_id="transfer")()

    extract >> transfer