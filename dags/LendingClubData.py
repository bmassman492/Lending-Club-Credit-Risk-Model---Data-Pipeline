from airflow.sdk import DAG, task
from datetime import datetime
from extractLendingClubDataScript import extract_data, transform_data

with DAG (
    dag_id="LendingClubData",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["extraction", "one-time"]
) as dag:
    
    
    extract = task(extract_data)()
    transform = task(transform_data)()
    
    
    
    #extract >>