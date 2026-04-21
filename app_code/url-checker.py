#!/usr/bin/env python3

import time
import requests
import os
from prometheus_client import start_http_server, Histogram, Counter, Gauge

CONFIGMAP_PATH = "/config/urls"

# Metrics
REQUEST_LATENCY = Histogram(
    "url_check_latency_seconds",
    "Latency of URL checks",
    ["url"],
    buckets=(0.1, 0.3, 0.5, 1, 2, 5, 10)
)

REQUEST_SUCCESS = Counter(
    "url_check_success_total",
    "Successful URL checks",
    ["url"]
)

REQUEST_FAILURE = Counter(
    "url_check_failure_total",
    "Failed URL checks",
    ["url"]
)

LAST_STATUS = Gauge(
    "url_last_status_code",
    "Last HTTP status code",
    ["url"]
)

def load_urls():
    try:
        with open(CONFIGMAP_PATH, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as exc:
        print(f"Error loading URLs: {exc}")
        return

def check_url(url):
    start = time.time()
    try:
        response = requests.get(url, timeout=5)
        latency = time.time() - start

        REQUEST_LATENCY.labels(url=url).observe(latency)
        LAST_STATUS.labels(url=url).set(response.status_code)

        if response.ok:
            REQUEST_SUCCESS.labels(url=url).inc()
        else:
            REQUEST_FAILURE.labels(url=url).inc()

    except Exception:
        latency = time.time() - start
        REQUEST_LATENCY.labels(url=url).observe(latency)
        REQUEST_FAILURE.labels(url=url).inc()
        LAST_STATUS.labels(url=url).set(0)

def main():
    # Expose metrics
    start_http_server(8000)

    while True:
        urls = load_urls()
        for url in urls:
            check_url(url)

        time.sleep(30)

if __name__ == "__main__":
    main()

