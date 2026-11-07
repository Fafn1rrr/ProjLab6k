from flask import Flask, jsonify

from db import DatabaseConfigurationError, get_connection

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({"message": "ProjLab6k demo backend"})


@app.get("/api/health")
def health():
    with get_connection() as conn:
        conn.execute("SELECT 1")

    return jsonify({"status": "ok"})
