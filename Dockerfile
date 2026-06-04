FROM apache/airflow:3.2.1-python3.12

USER airflow
COPY requirements.txt /requirements.txt
RUN grep -v "^dbt" /requirements.txt > /tmp/airflow-reqs.txt && \
    pip install --no-cache-dir -r /tmp/airflow-reqs.txt \
        --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.2.1/constraints-3.12.txt" && \
    grep "^dbt" /requirements.txt | xargs pip install --no-cache-dir
