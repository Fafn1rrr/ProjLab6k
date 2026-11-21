import math

import psycopg
from flask import Flask, jsonify, request, send_from_directory

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
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, profit_per_unit
                FROM books
                ORDER BY id
            """)
            rows = cur.fetchall()

    books = [
        {
            "id": row[0],
            "name": row[1],
            "profitPerUnit": float(row[2])
        }
        for row in rows
    ]

    return jsonify(books)


@app.post("/api/books")
def add_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    profit = data.get("profitPerUnit")

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Book name must have at least 2 characters."
        }), 400

    try:
        profit = float(profit)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Profit per unit must be a number."
        }), 400

    if profit < 0:
        return jsonify({
            "message": "Profit per unit cannot be negative."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (title, profit_per_unit)
                VALUES (%s, %s)
                RETURNING id
                """,
                (name.strip(), profit)
            )
            book_id = cur.fetchone()[0]

    return jsonify({
        "id": book_id,
        "name": name.strip(),
        "profitPerUnit": profit
    }), 201


@app.put("/api/books/<int:book_id>")
def update_book(book_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    profit = data.get("profitPerUnit")

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Book name must have at least 2 characters."
        }), 400

    try:
        profit = float(profit)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Profit per unit must be a number."
        }), 400

    if profit < 0:
        return jsonify({
            "message": "Profit per unit cannot be negative."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE books
                SET title = %s,
                    profit_per_unit = %s
                WHERE id = %s
                RETURNING id
                """,
                (name.strip(), profit, book_id)
            )

            updated = cur.fetchone()

    if updated is None:
        return jsonify({"message": "Book not found."}), 404

    return jsonify({
        "id": book_id,
        "name": name.strip(),
        "profitPerUnit": profit
    })


@app.get("/api/orders")
def get_orders():
    return jsonify([])


@app.get("/api/machines")
def get_machines():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, available_time
                FROM machines
                ORDER BY id
            """)
            rows = cur.fetchall()

    machines = [
        {
            "id": row[0],
            "name": row[1],
            "availableTime": float(row[2])
        }
        for row in rows
    ]

    return jsonify(machines)


@app.post("/api/machines")
def add_machine():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    available_time = data.get("availableTime")

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Machine name must have at least 2 characters."
        }), 400

    try:
        available_time = float(available_time)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Available time must be a number."
        }), 400

    if available_time <= 0:
        return jsonify({
            "message": "Available time must be greater than 0."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO machines (name, available_time)
                VALUES (%s, %s)
                RETURNING id
                """,
                (name.strip(), available_time)
            )
            machine_id = cur.fetchone()[0]

    return jsonify({
        "id": machine_id,
        "name": name.strip(),
        "availableTime": available_time
    }), 201


@app.put("/api/machines/<int:machine_id>")
def update_machine(machine_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    name = data.get("name")
    available_time = data.get("availableTime")

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "message": "Machine name must have at least 2 characters."
        }), 400

    try:
        available_time = float(available_time)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Available time must be a number."
        }), 400

    if available_time <= 0:
        return jsonify({
            "message": "Available time must be greater than 0."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE machines
                SET name = %s,
                    available_time = %s
                WHERE id = %s
                RETURNING id
                """,
                (name.strip(), available_time, machine_id)
            )

            updated = cur.fetchone()

    if updated is None:
        return jsonify({"message": "Machine not found."}), 404

    return jsonify({
        "id": machine_id,
        "name": name.strip(),
        "availableTime": available_time
    })

def is_integer_id(value):
    # bool is a subclass of int in Python, so True/False must be rejected explicitly.
    return isinstance(value, int) and not isinstance(value, bool)


@app.get("/api/processing-times")
def get_processing_times():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT book_id, machine_id, processing_time
                FROM processing_times
                ORDER BY book_id, machine_id
            """)
            rows = cur.fetchall()

    processing_times = [
        {
            "bookId": row[0],
            "machineId": row[1],
            "time": float(row[2])
        }
        for row in rows
    ]

    return jsonify(processing_times)


@app.put("/api/processing-times")
def upsert_processing_time():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON data."}), 400

    book_id = data.get("bookId")
    machine_id = data.get("machineId")
    time = data.get("time")

    if not is_integer_id(book_id):
        return jsonify({"message": "Book ID must be an integer."}), 400

    if not is_integer_id(machine_id):
        return jsonify({"message": "Machine ID must be an integer."}), 400

    if not isinstance(time, (int, float)) or isinstance(time, bool):
        return jsonify({"message": "Processing time must be a number."}), 400

    try:
        time = float(time)
    except OverflowError:
        return jsonify({"message": "Processing time is too large."}), 400

    # Python's JSON parser accepts NaN/Infinity; PostgreSQL NUMERIC would store NaN.
    if not math.isfinite(time):
        return jsonify({"message": "Processing time must be a number."}), 400

    if time < 0:
        return jsonify({
            "message": "Processing time must be 0 or greater."
        }), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM books WHERE id = %s", (book_id,))
            if cur.fetchone() is None:
                return jsonify({"message": "Book not found."}), 404

            cur.execute("SELECT 1 FROM machines WHERE id = %s", (machine_id,))
            if cur.fetchone() is None:
                return jsonify({"message": "Machine not found."}), 404

            try:
                cur.execute(
                    """
                    INSERT INTO processing_times
                        (book_id, machine_id, processing_time)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (book_id, machine_id)
                    DO UPDATE SET processing_time = EXCLUDED.processing_time
                    RETURNING processing_time
                    """,
                    (book_id, machine_id, time)
                )
            except psycopg.errors.NumericValueOutOfRange:
                conn.rollback()
                return jsonify({
                    "message": "Processing time is too large."
                }), 400

            # Return the value as stored (the column rounds to 4 decimals).
            stored_time = cur.fetchone()[0]

    return jsonify({
        "bookId": book_id,
        "machineId": machine_id,
        "time": float(stored_time)
    })


@app.errorhandler(DatabaseConfigurationError)
def handle_database_configuration_error(error):
    return jsonify({"message": str(error)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)