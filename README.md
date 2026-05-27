# Lending Club Credit Risk Model - Data Pipeline

## Project Overview
This project seeks to cover the entire data engineering pipeline and deliver a credit risk assessment model to lenders. The model will be a predictive machine learning model trained on real loans issued by Lending Club, with the target variable being loan outcome (how effectively the loan was paid off), as well as real macroeconomic time series data. 

## Data Sources

Lending Club real loan data: https://www.kaggle.com/datasets/wordsforthewise/lending-club




# How To Run

This is a portfolio project, but it can be run if desired using the following steps:

## Setting up .env

1) Copy .env.example as .env in the project root
2) Assign an Airflow Username and Password- this is what you will log in with when viewing DAGs in the browser
3) Generate a FERNET key and assign it to FERNET_KEY
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
4) Download the Lending Club dataset linked above, and add the filepath of accepted_2007_to_2018Q4.csv to .env
5) Setting up AWS variables:
   - Create account/log in at https://aws.amazon.com
   - Create a User at IAM -> Users -> Create User. When prompted for "Permission Options", select Attach Policies Directly and check AmazonS3FullAccess
   - Select the created user. Under Security Credentials, select Create Access Key. Add this key's id to AWS_ACCESS_KEY_ID and its value in AWS_SECRET_ACCESS_KEY in .env
   -Navigate to S3 "Create a bucket". Create the bucket, and assign its name to S3_BUCKET and AWS region to AWS_DEFAULT_REGION in .env
6) Setting up Snowflake variables:
   - Create account/log in at https://signup.snowflake.com
   - Assign SNOWFLAKE_USER and SNOWFLAKE_PASSWORD to the values creaded in signup
   - Locate account ID and assign it to SNOWFLAKE_ACCOUNT
   - Leave the remaining variables as is, select Workspaces -> Add New SQL file, and run:
```sql
CREATE WAREHOUSE IF NOT EXISTS credit_risk_assessment_wh
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;
```
```sql
CREATE DATABASE IF NOT EXISTS credit_risk_assessment_db;
```
```sql
CREATE SCHEMA IF NOT EXISTS credit_risk_assessment_db.raw;
```
```sql
CREATE SCHEMA IF NOT EXISTS credit_risk_assessment_db.transformed;
```

## Docker/Airflow Setup

1) Ensure Docker is installed (https://www.docker.com/):
```bash
docker compose version
```
2) (While in project root) Build airflow image 
```bash
docker compose build
docker compose up airflow-init
docker compose up -d 
```
3) View Airflow dags interface at localhost:8080 (log in using Airflow username and password from .env)

# References
Creating the docker-compose.yaml file with Airflow image (This doesn't need to be done again, as the .yaml file is already in the repository):
```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml'
```