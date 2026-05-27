import os
import boto3
import snowflake.connector


def extract_data():
    local_path = os.getenv("LENDING_CLUB_DATA_PATH")
    bucket = os.getenv("S3_BUCKET")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )

    s3.upload_file(local_path, bucket, "Raw_LC_Data.csv")

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
        schema="RAW",
    )

    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE OR REPLACE FILE FORMAT lc_csv_format
                TYPE = CSV
                SKIP_HEADER = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                NULL_IF = ('', 'NA', 'N/A')
        """)

        cur.execute(f"""
            CREATE OR REPLACE STAGE lc_s3_stage
                URL = 's3://{bucket}/'
                CREDENTIALS = (AWS_KEY_ID = '{aws_key}' AWS_SECRET_KEY = '{aws_secret}')
                FILE_FORMAT = lc_csv_format
        """)

        cur.execute("""
            CREATE OR REPLACE TABLE RAW_LC_DATA
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
                ON_ERROR = ABORT_STATEMENT
        """)
    finally:
        conn.close()
