from flask import Flask, jsonify, send_from_directory

from db import DatabaseConfigurationError, get_connection

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "planner.html")


@app.get("/api/health")
def health():
    with get_connection() as conn:
        conn.execute("SELECT 1")

    return jsonify({"status": "ok"})


@app.get("/api/books")
def get_books():
    return jsonify([])


@app.get("/api/orders")
def get_orders():
    return jsonify([])


@app.get("/api/machines")
def get_machines():
    return jsonify([])


@app.get("/api/processing-times")
def get_processing_times():
    return jsonify([])


@app.errorhandler(DatabaseConfigurationError)
def handle_database_configuration_error(error):
    return jsonify({"message": str(error)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)