FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py .

ENV MODEL_OUTPUT_DIR=/ml

CMD ["python", "train.py"]
