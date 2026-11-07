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

@app.get("/api/processing-times")
def get_processing_times():
    return jsonify([])


@app.errorhandler(DatabaseConfigurationError)
def handle_database_configuration_error(error):
    return jsonify({"message": str(error)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)