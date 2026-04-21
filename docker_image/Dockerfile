FROM python:3.11-slim

WORKDIR /url-checker

COPY url-checker.py .

RUN pip install --no-cache-dir prometheus_client requests

RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["python", "url-checker.py"]
