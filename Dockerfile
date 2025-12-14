FROM python:3.9-slim

WORKDIR /app

COPY simple_tracker.py .

# Environment variables
ENV TELEGRAM_BOT_TOKEN=7795627429:AAHdzjkww7WEUSXRsgG38rHMre4bMFG4mpw
ENV TELEGRAM_CHAT_ID=7155382465

CMD ["python3", "simple_tracker.py"]
