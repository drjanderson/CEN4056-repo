import os
import time
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- Configuration & Versioning ---
APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")
APP_ENV = os.getenv("APP_ENV", "development")
PORT = int(os.getenv("PORT", 5000))
SIMULATE_UNHEALTHY = os.getenv("SIMULATE_UNHEALTHY", "false").lower() == "true"

# --- Telemetry (Prometheus Metrics) ---
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

# In-memory store for fallback if DB is not attached
ITEMS_DB = ["Docker", "Kubernetes", "Prometheus"]


@app.before_request
def start_timer():
    request._start_time = time.time()


@app.after_request
def record_metrics(response):
    if hasattr(request, "_start_time") and request.path != "/metrics":
        latency = time.time() - request._start_time
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(latency)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
    return response


# --- Application Endpoints ---

@app.route("/")
def index():
    return jsonify({
        "message": "Welcome to the DevOps Baseline REST API",
        "version": APP_VERSION,
        "environment": APP_ENV
    }), 200


@app.route("/api/items", methods=["GET", "POST"])
def items():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        item = data.get("name")
        if not item:
            return jsonify({"error": "Item 'name' required"}), 400
        ITEMS_DB.append(item)
        return jsonify({"message": "Item added", "item": item}), 201

    return jsonify({"items": ITEMS_DB}), 200


@app.route("/health")
def health():
    """
    Health check endpoint for Kubernetes liveness & readiness probes.
    In Session 22, students simulate failures by returning HTTP 502.
    """
    if SIMULATE_UNHEALTHY:
        return jsonify({"status": "unhealthy", "reason": "Simulated poison payload"}), 502
    return jsonify({"status": "ok", "version": APP_VERSION}), 200


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)