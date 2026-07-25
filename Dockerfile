FROM python:3.12-slim

WORKDIR /app

COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ .

EXPOSE 5000

ENV AWS_DEFAULT_REGION=us-east-1

ENTRYPOINT ["python3", "app.py"]