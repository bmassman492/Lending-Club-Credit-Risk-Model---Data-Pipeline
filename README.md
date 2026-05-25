# Lending Club Credit Risk Model - Data Pipeline

## Project Overview
This project seeks to cover the entire data engineering pipeline and deliver a credit risk assessment model to lenders. The model will be a predictive machine learning model trained on real loans issued by Lending Club, with the target variable being loan outcome (how effectively the loan was paid off), as well as real macroeconomic time series data. 

## Data Sources



# How To Run

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
3) View Airflow dags interface at localhost:8080

## Dependencies


## Setting up .env