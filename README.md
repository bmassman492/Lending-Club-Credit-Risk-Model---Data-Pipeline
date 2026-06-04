# Lending Club Credit Risk Model - Data Pipeline

## Project Overview and Tech Stack
This project seeks to cover the entire data engineering ELT pipeline and deliver a credit risk assessment model to lenders. The model is a predictive XGBoost model trained on real loans issued by Lending Club and well as real macroeconomic time series data. The target variable is loan outcome, specifically if the borrower is likely to charge off the loan (outcome 1), or pay it off in full (outcome 0). 

Containerization: Docker

Orchestration: Apache Airflow

Cloud Data Lake/Warehousing: AWS S3, Snowflake

Data Transformation: dbt

ML Model: Python, XGBoost

API: Python FastAPI (REST API)

## Data Sources

Lending Club real loan data: https://www.kaggle.com/datasets/wordsforthewise/lending-club

The Lending Club dataset consists of roughly 2.5 million records of real loans given by Lending Club to borrowers. It includes several key pieces of information about the borrower's financial status and credit history, as well as the end result of the loan (e.g. Fully Paid, Charged Off).

FRED Macroeconomic Time-Series data: https://fred.stlouisfed.org/docs/api/fred/

FRED Macroeconomic data is acquired through an API hosted by the Federal Reserve Bank of Saint Louis, and contains information about the U.S. Economy that provides additional insight to borrower's credit trustworthiness at the time of the loan. 

## File Structure

```
├── api/
│   ├── app.py
│   ├── Dictionary.md
│   ├── Dockerfile
│   └── requirements.txt
├── config/
│   └── airflow.cfg
├── credit_risk_dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       │   ├── stg_lending_club.sql
│       │   ├── stg_fred_macroeconomic_data.sql
│       │   ├── schema.yml
│       │   └── _sources.yml
│       └── marts/
│           ├── fact_loans.sql
│           ├── dim_fred_macro_indicators.sql
│           └── schema.yml
├── dags/
│   ├── LendingClubData.py
│   ├── FREDMacroeconomic.py
│   └── TransformData.py
├── ml/
│   ├── Dockerfile
│   ├── model.pkl
│   ├── model_config.pkl
│   ├── requirements.txt
│   ├── train.py
│   └── trainModel.ipynb
├── scripts/
│   ├── extractLendingClubDataScript.py
│   └── extractFREDDataScript.py
├── .env.example
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

# How To Run

This is a portfolio project, but it can be run if desired by cloning the repository and following the below steps. To run the entire data ELT pipeline and model training process, continue from 'setting up .env'. To solely use the model/API, skip to model/API use

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
   - Assign SNOWFLAKE_USER and SNOWFLAKE_PASSWORD to the values created in signup
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
7) Get a FRED API key at https://fred.stlouisfed.org/docs/api/api_key.html and assign it to FRED_API_KEY

## Docker/Airflow Setup

1) Ensure Docker is installed (https://www.docker.com/) and running:
```bash
docker compose version
```
2) (While in project root) Build airflow image 
```bash
docker compose build
docker compose up airflow-init
docker compose up -d 
```
## Running ELT Pipeline

Once all environment variables have been set up and the docker container is running, extract, load, and transform the data by triggering the dags at the airflow UI (localhost:8080). 

Order: LendingClubData >> FREDMacroeconomicData >> dbt_transform

FREDMacroeconomicData and dbt_transform can be set to monthly recurrance or manually retriggered to ensure current macroeconomic data

## Training The Model

Build the ml-trainer docker image:
```bash
docker compose build ml-trainer
```

Finally, train the model This will take several minutes. The code for saving the model is commented out, as the model is already saved in this repository at ml/model.pkl and ml/model_config.pkl. Optionally, delete the .pkl files, uncomment the joblib.dump code at the end of train.py, and rerun.
```bash
docker compose --profile ml run --rm ml-trainer
```

## Model/API Use
1) If skipping to this step, ensure that docker is installed (https://www.docker.com/) and running:
```bash
docker compose version
```

2) Build the api docker image and start api server:
```bash
docker compose build api
docker compose up api
```
3) View information about the API and request/response body format at localhost:8000/docs

Here, you may also run a test request by selecting /predict >> "Try It Out"
```bash
{
  "LOAN_AMOUNT": 15000.0,
  "LOAN_TERM_MONTHS": 36,
  "LOAN_INTEREST_RATE": 26.30,
  "LOAN_PURPOSE_IS_DEBT_CONSOLIDATION": 1,
  "LOAN_EMP_LENGTH": 9,
  "LOAN_OWNS_HOME": 0,
  "LOAN_ANNUAL_INCOME": 75000,
  "LOAN_APPLYING_AS_INDIVIDUAL": 1,
  "LOAN_DTI": 12.93,
  "LOAN_FICO_RANGE_LOW": 665.0,
  "LOAN_EARLIEST_CR_LINE": 2001,
  "LOAN_OPEN_ACC": 7,
  "LOAN_DELINQ_2YRS": 2.0,
  "LOAN_INQ_LAST_6MTHS": 1.0,
  "LOAN_TOT_HI_CRED_LIM": 44592.0,
  "LOAN_TOTAL_BC_LIMIT": 22300.0,
  "LOAN_MORT_ACC": 0.0,
  "LOAN_BC_UTIL": 67.4,
  "GDP": 19692.595,
  "FEDERAL_FUNDS_RATE": 1.16,
  "FIXED_MORTGAGE_RATE": 3.94,
  "PERSONAL_SAVINGS_RATE": 6.1,
  "LOAN_PRIOR_DELINQUENCY": 1,
  "LOAN_PRIOR_RECORD": 0
}
```
4) View api/Dictionary.md for a list of term definitions 

# References
Creating the docker-compose.yaml file with Airflow image (This doesn't need to be done again, as the .yaml file is already in the repository):
```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml'
```

Testing a task in airflow dag:
```bash
docker compose exec airflow-scheduler airflow tasks test dag_id task_name todays_date
```

Navigating to schema in snowflake:
```bash
USE WAREHOUSE warehouse_name;
USE DATABASE database_name;
USE SCHEMA schema_name;
```