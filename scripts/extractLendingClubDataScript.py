import os
import boto3
import snowflake.connector
from botocore.exceptions import ClientError


def extract_data():
    local_path = "/opt/airflow/data/lending_club_raw.csv"
    bucket = os.getenv("S3_BUCKET")
    s3_key = "Raw_LC_Data.csv"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )

    try:
        s3.head_object(Bucket=bucket, Key=s3_key)
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise

    s3.upload_file(local_path, bucket, s3_key)

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
            CREATE FILE FORMAT IF NOT EXISTS lc_csv_format
                TYPE = CSV
                PARSE_HEADER = TRUE
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                NULL_IF = ('', 'NA', 'N/A')
        """)

        cur.execute(f"""
            CREATE STAGE IF NOT EXISTS lc_s3_stage
                URL = 's3://{bucket}/'
                CREDENTIALS = (AWS_KEY_ID = '{aws_key}' AWS_SECRET_KEY = '{aws_secret}')
                FILE_FORMAT = lc_csv_format
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS RAW_LC_DATA
                USING TEMPLATE (
                    SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                    FROM TABLE(
                        INFER_SCHEMA(
                            LOCATION => '@lc_s3_stage/Raw_LC_Data.csv',
                            FILE_FORMAT => 'lc_csv_format'
                        )
                    )
                )
        """)

        cur.execute("""
            COPY INTO RAW_LC_DATA
                FROM @lc_s3_stage/Raw_LC_Data.csv
                FILE_FORMAT = lc_csv_format
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                ON_ERROR = ABORT_STATEMENT
        """)
    finally:
        conn.close()
