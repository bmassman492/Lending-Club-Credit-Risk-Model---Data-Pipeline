import io
import os
import boto3
import pandas as pd
import snowflake.connector
from botocore.exceptions import ClientError
from fredapi import Fred


def extract_data():
    fred = Fred(api_key=os.getenv("FRED_API_KEY"))

    series_ids = ["UNRATE", "GDP", "FEDFUNDS", "CPIAUCSL", "MORTGAGE30US", "PSAVERT"]
    start_date = "2006-01-01"

    df = pd.DataFrame()
    for series_id in series_ids:
        df[series_id] = fred.get_series(series_id, observation_start=start_date)

    df = df.ffill().dropna()
    df.index.name = "DATE"
    df = df.reset_index()

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    s3.put_object(
        Bucket=os.getenv("S3_BUCKET"),
        Key="FRED_Macro_Data.csv",
        Body=csv_buffer.getvalue().encode("utf-8"),
    )


def transfer_data():
    bucket = os.getenv("S3_BUCKET")
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA_RAW"),
    )

    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE FILE FORMAT IF NOT EXISTS fred_csv_format
                TYPE = CSV
                PARSE_HEADER = TRUE
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                NULL_IF = ('', 'NA', 'N/A')
        """)

        cur.execute(f"""
            CREATE STAGE IF NOT EXISTS fred_s3_stage
                URL = 's3://{bucket}/'
                CREDENTIALS = (AWS_KEY_ID = '{aws_key}' AWS_SECRET_KEY = '{aws_secret}')
                FILE_FORMAT = fred_csv_format
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS RAW_FRED_DATA
                USING TEMPLATE (
                    SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                    FROM TABLE(
                        INFER_SCHEMA(
                            LOCATION => '@fred_s3_stage/FRED_Macro_Data.csv',
                            FILE_FORMAT => 'fred_csv_format'
                        )
                    )
                )
        """)

        cur.execute("TRUNCATE TABLE RAW_FRED_DATA")

        cur.execute("""
            COPY INTO RAW_FRED_DATA
                FROM @fred_s3_stage/FRED_Macro_Data.csv
                FILE_FORMAT = fred_csv_format
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                FORCE = TRUE
                ON_ERROR = ABORT_STATEMENT
        """)
    finally:
        conn.close()