FROM python:3.9-slim

WORKDIR /app

COPY simple_tracker.py .

CMD ["python3", "simple_tracker.py"]
